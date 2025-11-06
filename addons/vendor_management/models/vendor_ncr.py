# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class VendorNCR(models.Model):
    _name = 'vendor.ncr'
    _description = 'Non-Conformance Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_reported desc'

    name = fields.Char(string='NCR Number', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    vendor_id = fields.Many2one('vendor.vendor', string='Vendor', required=True, tracking=True, index=True)
    po_id = fields.Many2one('vendor.purchase.order', string='Purchase Order', tracking=True)
    grn_id = fields.Many2one('vendor.grn', string='GRN', tracking=True)

    date_reported = fields.Date(string='Report Date', default=fields.Date.today, required=True, tracking=True)
    reported_by_id = fields.Many2one('res.users', string='Reported By', default=lambda self: self.env.user, required=True)

    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity_rejected = fields.Float(string='Rejected Quantity', required=True)
    uom_id = fields.Many2one('uom.uom', string='UoM', required=True)

    ncr_type = fields.Selection([
        ('quality', 'Quality Issue'),
        ('quantity', 'Quantity Mismatch'),
        ('delivery', 'Delivery Issue'),
        ('packaging', 'Packaging Issue'),
        ('documentation', 'Documentation Issue'),
        ('other', 'Other')
    ], string='NCR Type', required=True, tracking=True)

    defect_category = fields.Selection([
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor')
    ], string='Severity', required=True, default='minor', tracking=True)

    description = fields.Text(string='Issue Description', required=True)
    root_cause = fields.Text(string='Root Cause Analysis')
    corrective_action = fields.Text(string='Corrective Action Required')

    vendor_response = fields.Text(string='Vendor Response')
    vendor_response_date = fields.Date(string='Response Date')

    resolution = fields.Text(string='Resolution')
    resolved_by_id = fields.Many2one('res.users', string='Resolved By')
    resolved_date = fields.Date(string='Resolution Date')

    financial_impact = fields.Monetary(string='Financial Impact', help='Cost due to NCR')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('reported', 'Reported'),
        ('vendor_notified', 'Vendor Notified'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', required=True, tracking=True)

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'NCR number must be unique!'),
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('vendor.ncr') or _('New')
        return super(VendorNCR, self).create(vals)

    def action_report(self):
        self.write({'state': 'reported'})

    def action_notify_vendor(self):
        self.write({'state': 'vendor_notified'})
        # Send notification to vendor
        self.vendor_id.message_post(
            body=_('NCR %s has been raised. Please review and respond.') % self.name,
            subject=_('Non-Conformance Report: %s') % self.name
        )

    def action_in_progress(self):
        self.write({'state': 'in_progress'})

    def action_resolve(self):
        self.write({
            'state': 'resolved',
            'resolved_by_id': self.env.user.id,
            'resolved_date': fields.Date.today()
        })

    def action_close(self):
        self.write({'state': 'closed'})
