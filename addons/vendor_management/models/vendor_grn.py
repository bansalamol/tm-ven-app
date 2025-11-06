# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VendorGRN(models.Model):
    _name = 'vendor.grn'
    _description = 'Goods Receipt Note'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_received desc'

    name = fields.Char(string='GRN Number', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    vendor_id = fields.Many2one('vendor.vendor', string='Vendor', required=True, tracking=True, index=True)
    po_id = fields.Many2one('vendor.purchase.order', string='Purchase Order', required=True, tracking=True)

    date_received = fields.Datetime(string='Receipt Date', default=fields.Datetime.now, required=True, tracking=True)
    received_by_id = fields.Many2one('res.users', string='Received By', default=lambda self: self.env.user, required=True)

    line_ids = fields.One2many('vendor.grn.line', 'grn_id', string='GRN Lines')

    delivery_challan_no = fields.Char(string='Delivery Challan No.')
    vehicle_number = fields.Char(string='Vehicle Number')
    transporter_name = fields.Char(string='Transporter Name')

    inspection_required = fields.Boolean(string='Inspection Required', default=True)
    inspection_status = fields.Selection([
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('partial', 'Partial')
    ], string='Inspection Status', default='pending', tracking=True)

    inspection_report_id = fields.Many2one('vendor.inspection.report', string='Inspection Report')
    inspection_remarks = fields.Text(string='Inspection Remarks')

    ncr_ids = fields.One2many('vendor.ncr', 'grn_id', string='NCRs')
    ncr_count = fields.Integer(string='NCR Count', compute='_compute_ncr_count')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('received', 'Received'),
        ('under_inspection', 'Under Inspection'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('partial', 'Partially Accepted')
    ], string='Status', default='draft', required=True, tracking=True)

    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'GRN number must be unique!'),
    ]

    def _compute_ncr_count(self):
        for grn in self:
            grn.ncr_count = len(grn.ncr_ids)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('vendor.grn') or _('New')
        result = super(VendorGRN, self).create(vals)
        # Update PO line quantities
        result._update_po_quantities()
        return result

    def _update_po_quantities(self):
        """Update received quantities in PO lines"""
        for grn in self:
            for line in grn.line_ids:
                if line.po_line_id:
                    line.po_line_id.qty_received += line.quantity_accepted

    def action_confirm_receipt(self):
        self.write({'state': 'received'})
        if self.inspection_required:
            self.write({'state': 'under_inspection'})

    def action_accept(self):
        self.write({
            'state': 'accepted',
            'inspection_status': 'passed'
        })

    def action_reject(self):
        self.write({
            'state': 'rejected',
            'inspection_status': 'failed'
        })

    def action_partial_accept(self):
        self.write({
            'state': 'partial',
            'inspection_status': 'partial'
        })

    def action_create_ncr(self):
        return {
            'name': _('Create NCR'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.ncr',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_vendor_id': self.vendor_id.id,
                'default_po_id': self.po_id.id,
                'default_grn_id': self.id
            },
        }


class VendorGRNLine(models.Model):
    _name = 'vendor.grn.line'
    _description = 'GRN Line'

    grn_id = fields.Many2one('vendor.grn', string='GRN', required=True, ondelete='cascade')
    po_line_id = fields.Many2one('vendor.purchase.order.line', string='PO Line', required=True)

    product_id = fields.Many2one(related='po_line_id.product_id', string='Product', readonly=True)
    description = fields.Text(related='po_line_id.description', string='Description', readonly=True)

    quantity_ordered = fields.Float(related='po_line_id.quantity', string='Ordered Qty', readonly=True)
    quantity_received = fields.Float(string='Received Qty', required=True)
    quantity_accepted = fields.Float(string='Accepted Qty')
    quantity_rejected = fields.Float(string='Rejected Qty')

    uom_id = fields.Many2one(related='po_line_id.uom_id', string='UoM', readonly=True)
    remarks = fields.Text(string='Remarks')

    @api.constrains('quantity_accepted', 'quantity_rejected', 'quantity_received')
    def _check_quantities(self):
        for line in self:
            if line.quantity_accepted + line.quantity_rejected != line.quantity_received:
                raise ValidationError(_('Accepted + Rejected quantity must equal received quantity.'))


class VendorInspectionReport(models.Model):
    _name = 'vendor.inspection.report'
    _description = 'Vendor Inspection Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Report Number', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    grn_id = fields.Many2one('vendor.grn', string='GRN', required=True)
    vendor_id = fields.Many2one(related='grn_id.vendor_id', string='Vendor', readonly=True)

    inspection_date = fields.Date(string='Inspection Date', default=fields.Date.today, required=True)
    inspector_id = fields.Many2one('res.users', string='Inspector', default=lambda self: self.env.user, required=True)

    inspection_criteria = fields.Text(string='Inspection Criteria')
    findings = fields.Text(string='Findings')
    result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('conditional', 'Conditional')
    ], string='Result', required=True)

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('vendor.inspection.report') or _('New')
        return super(VendorInspectionReport, self).create(vals)
