# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)

class PosReportZ(models.Model):
    _name = 'pos.report.z'
    _description = 'POS Z Report (Permanent)'
    # ... (fields remain the same) ...
    name = fields.Char(string='Report Name', required=True, readonly=True, default='/')
    session_id = fields.Many2one('pos.session', string='POS Session', required=True)
    start_date = fields.Datetime(string='Start Date', related='session_id.start_at', readonly=True)
    end_date = fields.Datetime(string='End Date', related='session_id.stop_at', readonly=True)
    total_sales = fields.Float(string='Total Sales')
    total_returns = fields.Float(string='Total Returns')
    net_sales = fields.Float(string='Net Sales')
    total_taxes = fields.Float(string='Total Taxes')
    total_discounts = fields.Float(string='Total Discounts')
    total_payments = fields.Float(string='Total Payments')
    total_items = fields.Integer(string="Total Items Sold")
    payment_details = fields.Text(string="Payment Details")
    category_details = fields.Text(string="Category Details")


class PosReportX(models.TransientModel):
    _name = 'pos.report.x'
    _description = 'POS X Report (Transient)'
    # ... (fields remain the same) ...
    name = fields.Char(string='Report Name', required=True, readonly=True)
    session_id = fields.Many2one('pos.session', string='POS Session', required=True)
    start_date = fields.Datetime(string='Start Date', related='session_id.start_at', readonly=True)
    end_date = fields.Datetime(string='Report Date', readonly=True, default=fields.Datetime.now)
    total_sales = fields.Float(string='Total Sales')
    total_returns = fields.Float(string='Total Returns')
    net_sales = fields.Float(string='Net Sales')
    total_taxes = fields.Float(string='Total Taxes')
    total_discounts = fields.Float(string='Total Discounts')
    total_payments = fields.Float(string='Total Payments')
    total_items = fields.Integer(string="Total Items Sold")
    payment_details = fields.Text(string="Payment Details")
    category_details = fields.Text(string="Category Details")

class PosSession(models.Model):
    _inherit = 'pos.session'

    # ... (calculation methods remain the same) ...
    def _calculate_financial_summary(self, orders):
        return {
            'total_sales': sum(o.amount_total for o in orders if o.amount_total >= 0),
            'total_returns': sum(abs(o.amount_total) for o in orders if o.amount_total < 0),
            'net_sales': sum(o.amount_total for o in orders),
            'total_taxes': sum(o.amount_tax for o in orders),
            'total_discounts': sum(sum(l.price_unit * l.qty * (l.discount / 100) for l in o.lines) for o in orders),
            'total_payments': sum(p.amount for p in orders.mapped('payment_ids')),
        }

    def _calculate_detailed_summary(self, orders):
        payment_methods = {}
        for payment in orders.mapped('payment_ids'):
            method_name = payment.payment_method_id.name
            payment_methods.setdefault(method_name, 0.0)
            payment_methods[method_name] += payment.amount
        category_summary = {}
        total_items = 0
        for line in orders.mapped('lines'):
            if line.qty > 0:
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

    # Frontend methods remain the same
    def generate_z_report(self):
        self.ensure_one()
        orders = self.order_ids
        financial_data = self._calculate_financial_summary(orders)
        detailed_data = self._calculate_detailed_summary(orders)
        report_data = {**financial_data, **detailed_data}
        report_data.update({'session_id': self.id, 'name': _("Z Report - %s") % self.name})
        report = self.env['pos.report.x'].create(report_data)
        return self.env.ref('bsr_xz_report.action_report_pos_z_detailed').report_action(report)

    def generate_x_report(self):
        self.ensure_one()
        orders = self.order_ids
        report_data = self._calculate_financial_summary(orders)
        report_data.update({'session_id': self.id, 'name': _("X Report - %s") % self.name})
        report = self.env['pos.report.x'].create(report_data)
        return self.env.ref('bsr_xz_report.action_report_pos_x').report_action(report)

    def action_pos_session_closing_control(self):
        res = super(PosSession, self).action_pos_session_closing_control()
        for session in self:
            try:
                if not self.env['pos.report.z'].search([('session_id', '=', session.id)]):
                    orders = session.order_ids
                    financial_data = self._calculate_financial_summary(orders)
                    detailed_data = self._calculate_detailed_summary(orders)
                    report_data = {**financial_data, **detailed_data}
                    report_data.update({'session_id': session.id, 'name': _("Z Report - %s") % session.name})
                    self.env['pos.report.z'].create(report_data)
            except Exception as e:
                _logger.error("Could not create Z Report for session %s: %s", session.name, e)
        return res

    def _prepare_backend_preview_vals(self, data):
        """Prepares the dictionary of values for the backend preview wizard."""
        payment_lines = [(0, 0, {'name': p['name'], 'amount': p['amount']}) for p in data.get('payment_details', [])]
        category_lines = [(0, 0, {'name': c['name'], 'quantity': c['qty'], 'amount': c['amount']}) for c in data.get('category_details', [])]

        return {
            'session_id': self.id,
            'report_title': data.get('report_title'),
            'report_date': data.get('report_date'),
            'is_z_report': data.get('is_z_report', False),
            'total_sales': data.get('total_sales'),
            'total_returns': data.get('total_returns'),
            'net_sales': data.get('net_sales'),
            'total_taxes': data.get('total_taxes'),
            'total_discounts': data.get('total_discounts'),
            'total_payments': data.get('total_payments'),
            'total_items': data.get('total_items'),
            'payment_lines': payment_lines,
            'category_lines': category_lines,
        }

    def _open_backend_preview_wizard(self, preview_vals):
        """Opens the backend preview wizard with the provided values."""
        preview_wizard = self.env['bsr.pos.backend.report.preview'].create(preview_vals)
        return {
            'name': _('Report Preview'),
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.pos.backend.report.preview',
            'view_mode': 'form',
            'res_id': preview_wizard.id,
            'target': 'new',
        }

    def print_z_report_backend(self):
        """ Replaces direct printing with opening a preview wizard for the Z Report. """
        self.ensure_one()
        report_z = self.env['pos.report.z'].search([('session_id', '=', self.id)], limit=1)
        if not report_z:
            raise UserError(_("No Z Report has been saved for this session. It is generated upon closing."))

        data = {
            'report_title': report_z.name,
            'report_date': report_z.session_id.stop_at,
            'is_z_report': True,
            'total_sales': report_z.total_sales,
            'total_returns': report_z.total_returns,
            'net_sales': report_z.net_sales,
            'total_taxes': report_z.total_taxes,
            'total_discounts': report_z.total_discounts,
            'total_payments': report_z.total_payments,
            'total_items': report_z.total_items,
            'payment_details': json.loads(report_z.payment_details),
            'category_details': json.loads(report_z.category_details),
        }

        preview_vals = self._prepare_backend_preview_vals(data)
        return self._open_backend_preview_wizard(preview_vals)

    # Overwrite generate_x_report to open the wizard instead of printing
    def generate_x_report(self):
        self.ensure_one()
        if self.env.context.get('from_backend'):
            data = self.get_x_report_data()
            preview_vals = self._prepare_backend_preview_vals(data)
            return self._open_backend_preview_wizard(preview_vals)
        return super(PosSession, self).generate_x_report()

    # Modify the button method in pos_session_view to call the wizard with context
    def button_generate_x_report(self):
        return self.with_context(from_backend=True).generate_x_report()

    # Data-fetching methods for frontend
    def get_x_report_data(self):
        self.ensure_one()
        orders = self.order_ids
        report_data = self._calculate_financial_summary(orders)
        report_data.update({
            'session_name': self.name, 'currency_symbol': self.currency_id.symbol,
            'report_title': _("X Report - %s") % self.name, 'report_date': fields.Datetime.now(),
            'is_z_report': False
        })
        return report_data

    def get_z_report_data(self):
        self.ensure_one()
        orders = self.order_ids
        financial_data = self._calculate_financial_summary(orders)
        detailed_data = self._calculate_detailed_summary(orders)
        report_data = {**financial_data, **detailed_data}
        report_data.update({
            'session_name': self.name, 'currency_symbol': self.currency_id.symbol,
            'report_title': _("Z Report - %s") % self.name, 'report_date': fields.Datetime.now(),
            'is_z_report': True
        })
        report_data['payment_details'] = json.loads(report_data['payment_details'])
        report_data['category_details'] = json.loads(report_data['category_details'])
        return report_data
