# -*- coding: utf-8 -*-

from odoo import models, fields

class BackendReportPreview(models.TransientModel):
    _name = 'bsr.pos.backend.report.preview'
    _description = 'POS Backend Report Preview Wizard'

    session_id = fields.Many2one('pos.session', string='Session', readonly=True)
    report_title = fields.Char(string="Report Title", readonly=True)
    report_date = fields.Datetime(string="Report Date", readonly=True)
    is_z_report = fields.Boolean(readonly=True)

    # Financial Summary
    total_sales = fields.Float(string='Total Sales', readonly=True)
    total_returns = fields.Float(string='Total Returns', readonly=True)
    net_sales = fields.Float(string='Net Sales', readonly=True)
    total_taxes = fields.Float(string='Total Taxes', readonly=True)
    total_discounts = fields.Float(string='Total Discounts', readonly=True)
    total_payments = fields.Float(string='Total Payments', readonly=True)

    # Detailed Summary
    total_items = fields.Integer(string="Total Items Sold", readonly=True)
    payment_lines = fields.One2many('bsr.pos.backend.payment.line', 'preview_id', string="Payment Lines", readonly=True)
    category_lines = fields.One2many('bsr.pos.backend.category.line', 'preview_id', string="Category Lines", readonly=True)

    def action_print_report(self):
        """ Called from the 'Print PDF' button in the wizard.
        It triggers the original PDF report generation.
        """
        self.ensure_one()
        if self.is_z_report:
            # For Z-Report, we print the permanent, detailed one
            report = self.env['pos.report.z'].search([('session_id', '=', self.session_id.id)], limit=1)
            if not report:
                raise UserError(_("Could not find the saved Z Report to print."))
            return self.env.ref('bsr_xz_report.action_report_pos_z_permanent').report_action(report)
        else:
            # For X-Report, we generate a fresh, simple one
            return self.session_id.generate_x_report()

class BackendPaymentLine(models.TransientModel):
    _name = 'bsr.pos.backend.payment.line'
    _description = 'POS Backend Report Payment Line'

    preview_id = fields.Many2one('bsr.pos.backend.report.preview', required=True, ondelete='cascade')
    name = fields.Char(string="Payment Method", readonly=True)
    amount = fields.Float(string="Amount", readonly=True)

class BackendCategoryLine(models.TransientModel):
    _name = 'bsr.pos.backend.category.line'
    _description = 'POS Backend Report Category Line'

    preview_id = fields.Many2one('bsr.pos.backend.report.preview', required=True, ondelete='cascade')
    name = fields.Char(string="Category", readonly=True)
    quantity = fields.Integer(string="Quantity", readonly=True)
    amount = fields.Float(string="Amount", readonly=True)
