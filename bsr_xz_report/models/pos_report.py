# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json

class PosReportZ(models.Model):
    _name = 'pos.report.z'
    _description = 'POS Z Report (Permanent)'

    name = fields.Char(string='Report Name', required=True, readonly=True, default='/')
    session_id = fields.Many2one('pos.session', string='POS Session', required=True)
    start_date = fields.Datetime(string='Start Date', related='session_id.start_at', readonly=True)
    end_date = fields.Datetime(string='End Date', related='session_id.stop_at', readonly=True)

    # Financial Summary
    total_sales = fields.Float(string='Total Sales')
    total_returns = fields.Float(string='Total Returns')
    net_sales = fields.Float(string='Net Sales')
    total_taxes = fields.Float(string='Total Taxes')
    total_discounts = fields.Float(string='Total Discounts')
    total_payments = fields.Float(string='Total Payments')

    # Detailed Summary
    total_items = fields.Integer(string="Total Items Sold")
    payment_details = fields.Text(string="Payment Details")
    category_details = fields.Text(string="Category Details")


class PosReportX(models.TransientModel):
    _name = 'pos.report.x'
    _description = 'POS X Report (Transient)'

    name = fields.Char(string='Report Name', required=True, readonly=True)
    session_id = fields.Many2one('pos.session', string='POS Session', required=True)
    start_date = fields.Datetime(string='Start Date', related='session_id.start_at', readonly=True)
    end_date = fields.Datetime(string='Report Date', readonly=True, default=fields.Datetime.now)

    # Financial Summary
    total_sales = fields.Float(string='Total Sales')
    total_returns = fields.Float(string='Total Returns')
    net_sales = fields.Float(string='Net Sales')
    total_taxes = fields.Float(string='Total Taxes')
    total_discounts = fields.Float(string='Total Discounts')
    total_payments = fields.Float(string='Total Payments')

    # Detailed Summary (matching Z report for detailed printing)
    total_items = fields.Integer(string="Total Items Sold")
    payment_details = fields.Text(string="Payment Details")
    category_details = fields.Text(string="Category Details")

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _calculate_financial_summary(self, orders):
        """Helper method to calculate the main financial figures."""
        return {
            'total_sales': sum(o.amount_total for o in orders if o.amount_total >= 0),
            'total_returns': sum(abs(o.amount_total) for o in orders if o.amount_total < 0),
            'net_sales': sum(o.amount_total for o in orders),
            'total_taxes': sum(o.amount_tax for o in orders),
            'total_discounts': sum(sum(l.price_unit * l.qty * (l.discount / 100) for l in o.lines) for o in orders),
            'total_payments': sum(p.amount for p in orders.mapped('payment_ids')),
        }

    def _calculate_detailed_summary(self, orders):
        """Helper method to calculate detailed sales data."""
        # Payment Details
        payment_methods = {}
        for payment in orders.mapped('payment_ids'):
            method_name = payment.payment_method_id.name
            payment_methods.setdefault(method_name, 0.0)
            payment_methods[method_name] += payment.amount

        # Category and Item Details
        category_summary = {}
        total_items = 0
        for line in orders.mapped('lines'):
            if line.qty > 0: # Exclude returned items from totals
                category_name = line.product_id.pos_categ_id.name or 'Uncategorized'
                category_summary.setdefault(category_name, {'qty': 0, 'amount': 0.0})
                category_summary[category_name]['qty'] += line.qty
                category_summary[category_name]['amount'] += line.price_subtotal_incl
                total_items += line.qty

        return {
            'total_items': total_items,
            'payment_details': json.dumps([{'name': name, 'amount': amount} for name, amount in payment_methods.items()]),
            'category_details': json.dumps([{'name': name, 'qty': data['qty'], 'amount': data['amount']} for name, data in category_summary.items()]),
        }

    def generate_z_report(self):
        """ This method is called from the POS frontend.
        It prints a DETAILED Z Report for the CURRENTLY OPEN session.
        """
        self.ensure_one()
        orders = self.order_ids

        financial_data = self._calculate_financial_summary(orders)
        detailed_data = self._calculate_detailed_summary(orders)

        report_data = {**financial_data, **detailed_data}

        # The Z-Report from the frontend is now a transient, detailed report.
        # The permanent, simpler Z report is created on closing.
        report_data.update({
            'session_id': self.id,
            'name': _("Z Report - %s") % self.name,
        })

        report = self.env['pos.report.x'].create(report_data) # Use the transient model for printing
        return self.env.ref('bsr_xz_report.action_report_pos_z_detailed').report_action(report)

    def generate_x_report(self):
        """ This method is called from the POS frontend.
        It prints a SIMPLE X Report (financial summary) for the CURRENTLY OPEN session.
        """
        self.ensure_one()
        orders = self.order_ids
        report_data = self._calculate_financial_summary(orders)
        report_data.update({
            'session_id': self.id,
            'name': _("X Report - %s") % self.name,
        })

        report = self.env['pos.report.x'].create(report_data)
        return self.env.ref('bsr_xz_report.action_report_pos_x').report_action(report)

    def action_pos_session_closing_control(self):
        """ Inherited to automatically create the permanent, simple Z Report on session closing. """
        res = super(PosSession, self).action_pos_session_closing_control()
        for session in self:
            report = self.env['pos.report.z'].search([('session_id', '=', session.id)], limit=1)
            if not report:
                orders = session.order_ids
                financial_data = self._calculate_financial_summary(orders)
                detailed_data = self._calculate_detailed_summary(orders)
                report_data = {**financial_data, **detailed_data}

                report_data.update({
                    'session_id': session.id,
                    'name': _("Z Report - %s") % session.name,
                })
                self.env['pos.report.z'].create(report_data)
        return res

    def print_z_report_backend(self):
        """ This method is called from the backend session form view.
        It prints the permanent Z Report associated with the session.
        """
        self.ensure_one()
        report = self.env['pos.report.z'].search([('session_id', '=', self.id)], limit=1)
        if not report:
            raise UserError(_("No Z Report has been saved for this session. It is generated upon closing."))

        # We need to use a different report action that points to the correct model
        return self.env.ref('bsr_xz_report.action_report_pos_z_permanent').report_action(report)

    def get_x_report_data(self):
        """ Returns a JSON dictionary with the data for the X-Report preview. """
        self.ensure_one()
        orders = self.order_ids
        report_data = self._calculate_financial_summary(orders)

        # Add extra info for the preview popup
        report_data['session_name'] = self.name
        report_data['currency_symbol'] = self.currency_id.symbol
        report_data['report_title'] = _("X Report - %s") % self.name
        report_data['report_date'] = fields.Datetime.now()
        report_data['is_z_report'] = False
        return report_data

    def get_z_report_data(self):
        """ Returns a JSON dictionary with the data for the Z-Report preview. """
        self.ensure_one()
        orders = self.order_ids
        financial_data = self._calculate_financial_summary(orders)
        detailed_data = self._calculate_detailed_summary(orders)

        report_data = {**financial_data, **detailed_data}

        # Add extra info for the preview popup
        report_data['session_name'] = self.name
        report_data['currency_symbol'] = self.currency_id.symbol
        report_data['report_title'] = _("Z Report - %s") % self.name
        report_data['report_date'] = fields.Datetime.now()
        report_data['is_z_report'] = True

        # Decode the JSON fields to be sent as a structured dictionary
        report_data['payment_details'] = json.loads(report_data['payment_details'])
        report_data['category_details'] = json.loads(report_data['category_details'])
        return report_data
