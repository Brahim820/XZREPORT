# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TreasuryForecast(models.Model):
    _name = 'treasury.forecast'
    _description = 'Treasury Forecast'

    name = fields.Char(string='Name', required=True)
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)
    line_ids = fields.One2many('treasury.forecast.line', 'forecast_id', string='Forecast Lines')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    def calculate_forecast(self):
        for forecast in self:
            forecast.line_ids.unlink()
            company = forecast.company_id
            currency = company.currency_id

            # Initial Balance
            journals = self.env['account.journal'].search([('type', 'in', ['bank', 'cash']), ('company_id', '=', company.id)])
            self.env.cr.execute("""
                SELECT SUM(aml.balance)
                FROM account_move_line aml
                JOIN account_move am ON am.id = aml.move_id
                WHERE aml.date < %s AND am.state = 'posted' AND aml.journal_id = ANY(%s)
            """, (forecast.date_start, journals.ids))
            initial_balance = self.env.cr.fetchone()[0] or 0.0

            forecast.line_ids.create({
                'forecast_id': forecast.id,
                'date': forecast.date_start,
                'description': 'Initial Balance',
                'amount': initial_balance,
            })

            # Customer Invoices
            invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'), ('state', '=', 'posted'),
                ('invoice_date_due', '>=', forecast.date_start), ('invoice_date_due', '<=', forecast.date_end),
                ('company_id', '=', company.id)
            ])
            for invoice in invoices:
                forecast.line_ids.create({
                    'forecast_id': forecast.id,
                    'date': invoice.invoice_date_due,
                    'description': invoice.name,
                    'amount': invoice.amount_total,
                })

            # Vendor Bills
            bills = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'), ('state', '=', 'posted'),
                ('invoice_date_due', '>=', forecast.date_start), ('invoice_date_due', '<=', forecast.date_end),
                ('company_id', '=', company.id)
            ])
            for bill in bills:
                forecast.line_ids.create({
                    'forecast_id': forecast.id,
                    'date': bill.invoice_date_due,
                    'description': bill.name,
                    'amount': -bill.amount_total,
                })

class TreasuryForecastLine(models.Model):
    _name = 'treasury.forecast.line'
    _description = 'Treasury Forecast Line'
    _order = 'date'

    date = fields.Date(string='Date', required=True)
    amount = fields.Float(string='Amount', required=True)
    description = fields.Char(string='Description')
    forecast_id = fields.Many2one('treasury.forecast', string='Forecast', required=True, ondelete='cascade')
    balance = fields.Float(string='Balance', compute='_compute_balance', store=True)

    @api.depends('amount', 'forecast_id.line_ids.amount')
    def _compute_balance(self):
        for forecast in self.mapped('forecast_id'):
            balance = 0.0
            for line in forecast.line_ids:
                balance += line.amount
                line.balance = balance
