# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VendorQuotation(models.Model):
    _name = 'vendor.quotation'
    _description = 'Vendor Quotation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_submitted desc'

    name = fields.Char(string='Quotation Number', compute='_compute_name', store=True)
    rfq_id = fields.Many2one('vendor.rfq', string='RFQ', required=True, ondelete='cascade', tracking=True)
    vendor_id = fields.Many2one('vendor.vendor', string='Vendor', required=True, tracking=True)

    date_submitted = fields.Date(string='Submission Date', tracking=True)
    valid_until = fields.Date(string='Valid Until', tracking=True)

    line_ids = fields.One2many('vendor.quotation.line', 'quotation_id', string='Quotation Lines')

    total_amount = fields.Monetary(string='Total Amount', compute='_compute_total_amount', store=True)
    currency_id = fields.Many2one(related='rfq_id.currency_id', string='Currency')

    payment_terms = fields.Text(string='Payment Terms')
    delivery_terms = fields.Text(string='Delivery Terms')
    warranty_terms = fields.Text(string='Warranty Terms')
    notes = fields.Text(string='Additional Notes')

    # Technical Evaluation
    technical_score = fields.Float(string='Technical Score', help='Score out of 100')
    technical_remarks = fields.Text(string='Technical Remarks')

    # Commercial Evaluation
    commercial_score = fields.Float(string='Commercial Score', help='Score out of 100')
    commercial_remarks = fields.Text(string='Commercial Remarks')

    # Overall Evaluation
    overall_score = fields.Float(string='Overall Score', compute='_compute_overall_score', store=True)
    evaluation_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Evaluation Status', default='not_started')

    evaluated_by_id = fields.Many2one('res.users', string='Evaluated By')
    evaluation_date = fields.Date(string='Evaluation Date')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_evaluation', 'Under Evaluation'),
        ('awarded', 'Awarded'),
        ('lost', 'Lost'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    @api.depends('rfq_id', 'vendor_id')
    def _compute_name(self):
        for quotation in self:
            if quotation.rfq_id and quotation.vendor_id:
                quotation.name = f"{quotation.rfq_id.name}/{quotation.vendor_id.code}"
            else:
                quotation.name = _('New')

    @api.depends('line_ids', 'line_ids.subtotal')
    def _compute_total_amount(self):
        for quotation in self:
            quotation.total_amount = sum(quotation.line_ids.mapped('subtotal'))

    @api.depends('technical_score', 'commercial_score')
    def _compute_overall_score(self):
        for quotation in self:
            if quotation.technical_score or quotation.commercial_score:
                # 60% weightage to technical, 40% to commercial
                quotation.overall_score = (quotation.technical_score * 0.6) + (quotation.commercial_score * 0.4)
            else:
                quotation.overall_score = 0.0

    def action_submit(self):
        self.write({
            'state': 'submitted',
            'date_submitted': fields.Date.today()
        })
        # Notify RFQ requester
        self.rfq_id.message_post(
            body=_('Quotation received from %s') % self.vendor_id.name,
            subject=_('New Quotation Received')
        )

    def action_start_evaluation(self):
        self.write({
            'state': 'under_evaluation',
            'evaluation_status': 'in_progress'
        })

    def action_complete_evaluation(self):
        if not self.technical_score or not self.commercial_score:
            raise ValidationError(_('Please complete both technical and commercial evaluation scores.'))

        self.write({
            'evaluation_status': 'completed',
            'evaluated_by_id': self.env.user.id,
            'evaluation_date': fields.Date.today()
        })


class VendorQuotationLine(models.Model):
    _name = 'vendor.quotation.line'
    _description = 'Vendor Quotation Line'
    _order = 'sequence, id'

    quotation_id = fields.Many2one('vendor.quotation', string='Quotation', required=True, ondelete='cascade')
    rfq_line_id = fields.Many2one('vendor.rfq.line', string='RFQ Line', required=True)

    sequence = fields.Integer(related='rfq_line_id.sequence', store=True)
    product_id = fields.Many2one(related='rfq_line_id.product_id', string='Product', readonly=True)
    description = fields.Text(related='rfq_line_id.description', string='Description', readonly=True)

    quantity = fields.Float(related='rfq_line_id.quantity', string='Quantity', readonly=True)
    uom_id = fields.Many2one(related='rfq_line_id.uom_id', string='UoM', readonly=True)

    unit_price = fields.Float(string='Unit Price', required=True)
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_subtotal', store=True)

    currency_id = fields.Many2one(related='quotation_id.currency_id', string='Currency')

    delivery_lead_time = fields.Integer(string='Delivery Lead Time (Days)')
    remarks = fields.Text(string='Remarks')

    @api.depends('quantity', 'unit_price', 'tax_ids')
    def _compute_subtotal(self):
        for line in self:
            price = line.unit_price * line.quantity
            if line.tax_ids:
                taxes = line.tax_ids.compute_all(line.unit_price, line.currency_id, line.quantity)
                line.subtotal = taxes['total_included']
            else:
                line.subtotal = price
