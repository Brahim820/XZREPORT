# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PosReportZ(models.Model):
    _name = 'pos.report.z'
    _description = 'POS Z Report (Permanent)'

    name = fields.Char(string='Report Name', required=True, readonly=True, default='/')
    session_id = fields.Many2one('pos.session', string='POS Session', required=True)
    start_date = fields.Datetime(string='Start Date', related='session_id.start_at', readonly=True)
    end_date = fields.Datetime(string='End Date', related='session_id.stop_at', readonly=True)
    total_sales = fields.Float(string='Total Sales')
    total_payments = fields.Float(string='Total Payments')
    total_taxes = fields.Float(string='Total Taxes')
    total_discounts = fields.Float(string='Total Discounts')
    total_returns = fields.Float(string='Total Returns')
    net_sales = fields.Float(string='Net Sales')

class PosReportX(models.TransientModel):
    _name = 'pos.report.x'
    _description = 'POS X Report (Transient)'

    name = fields.Char(string='Report Name', required=True, readonly=True)
    session_id = fields.Many2one('pos.session', string='POS Session', required=True)
    start_date = fields.Datetime(string='Start Date', related='session_id.start_at', readonly=True)
    end_date = fields.Datetime(string='Report Date', readonly=True, default=fields.Datetime.now)
    total_sales = fields.Float(string='Total Sales')
    total_payments = fields.Float(string='Total Payments')
    total_taxes = fields.Float(string='Total Taxes')
    total_discounts = fields.Float(string='Total Discounts')
    total_returns = fields.Float(string='Total Returns')
    net_sales = fields.Float(string='Net Sales')


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _calculate_report_data(self):
        """Helper method to calculate sales data for the session."""
        self.ensure_one()
        orders = self.order_ids

        total_sales = sum(order.amount_total for order in orders if order.amount_total >= 0)
        total_payments = sum(payment.amount for payment in orders.mapped('payment_ids'))
        total_taxes = sum(orders.mapped('amount_tax'))
        total_discounts = sum(line.price_unit * line.qty * (line.discount / 100) for line in orders.mapped('lines'))
        total_returns = sum(abs(order.amount_total) for order in orders if order.amount_total < 0)
        net_sales = total_sales - total_returns

        return {
            'total_sales': total_sales,
            'total_payments': total_payments,
            'total_taxes': total_taxes,
            'total_discounts': total_discounts,
            'total_returns': total_returns,
            'net_sales': net_sales,
        }

    def generate_z_report(self):
        self.ensure_one()
        if self.state != 'closed':
            raise UserError(_("You must close the session to generate the Z report."))

        report = self.env['pos.report.z'].search([('session_id', '=', self.id)], limit=1)
        if not report:
            report_data = self._calculate_report_data()
            report_data.update({
                'session_id': self.id,
                'name': f"Z Report - {self.name}"
            })
            report = self.env['pos.report.z'].create(report_data)

        return self.env.ref('bsr_xz_report.action_report_pos_z').report_action(report)


    def generate_x_report(self):
        self.ensure_one()
        report_data = self._calculate_report_data()
        report_data.update({
            'session_id': self.id,
            'name': f"X Report - {self.name}"
        })

        report = self.env['pos.report.x'].create(report_data)
        return self.env.ref('bsr_xz_report.action_report_pos_x').report_action(report)
