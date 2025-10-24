# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PosReport(models.Model):
    _name = 'pos.report.z'
    _description = 'POS Z Reports'

    name = fields.Char(string='Report Name', required=True, readonly=True, default='/')
    session_id = fields.Many2one('pos.session', string='POS Session', required=True)
    start_date = fields.Datetime(string='Start Date', related='session_id.start_at', readonly=True)
    end_date = fields.Datetime(string='End Date', related='session_id.stop_at', readonly=True)
    total_sales = fields.Float(string='Total Sales', compute='_compute_report_data')
    total_payments = fields.Float(string='Total Payments', compute='_compute_report_data')
    total_taxes = fields.Float(string='Total Taxes', compute='_compute_report_data')
    total_discounts = fields.Float(string='Total Discounts', compute='_compute_report_data')
    total_returns = fields.Float(string='Total Returns', compute='_compute_report_data')
    net_sales = fields.Float(string='Net Sales', compute='_compute_report_data')

    @api.depends('session_id')
    def _compute_report_data(self):
        for report in self:
            orders = self.env['pos.order'].search([('session_id', '=', report.session_id.id)])

            total_sales = sum(orders.mapped('amount_total'))
            total_payments = sum(payment.amount for payment in orders.mapped('payment_ids'))
            total_taxes = sum(orders.mapped('amount_tax'))
            total_discounts = sum(line.price_unit * line.qty * (line.discount / 100) for line in orders.mapped('lines'))

            # Simple return calculation
            total_returns = sum(abs(order.amount_total) for order in orders if order.amount_total < 0)

            report.total_sales = total_sales
            report.total_payments = total_payments
            report.total_taxes = total_taxes
            report.total_discounts = total_discounts
            report.total_returns = total_returns
            report.net_sales = total_sales - total_returns

class PosSession(models.Model):
    _inherit = 'pos.session'

    def generate_z_report(self):
        if self.state != 'closed':
            raise UserError(_("You must close the session to generate the Z report."))

        report = self.env['pos.report.z'].create({'session_id': self.id})
        report.name = f"Z Report - {self.name}"

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pos.report.z',
            'view_mode': 'form',
            'res_id': report.id,
            'target': 'new',
        }

    def generate_x_report(self):
        # For X report, we will just print the current state without creating a permanent record
        orders = self.env['pos.order'].search([('session_id', '=', self.id)])

        # This is a simplified version. A real implementation might create a transient model
        # or pass data directly to the report action.
        # For now, we will raise a placeholder message.
        raise UserError(_("X Report functionality is not fully implemented in this version."))
