# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class VendorChecklist(models.Model):
    _name = 'vendor.checklist'
    _description = 'Vendor Pre-qualification Checklist'
    _order = 'sequence, id'

    vendor_id = fields.Many2one('vendor.vendor', string='Vendor', required=True, ondelete='cascade', index=True)
    checklist_template_id = fields.Many2one('vendor.checklist.template', string='Checklist Item', required=True)
    name = fields.Char(related='checklist_template_id.name', string='Checklist Item', readonly=True)
    description = fields.Text(related='checklist_template_id.description', readonly=True)
    category = fields.Selection(related='checklist_template_id.category', readonly=True)
    sequence = fields.Integer(related='checklist_template_id.sequence', readonly=True, store=True)

    completed = fields.Boolean(string='Completed', tracking=True)
    completed_by_id = fields.Many2one('res.users', string='Completed By', tracking=True)
    completed_date = fields.Date(string='Completion Date', tracking=True)
    remarks = fields.Text(string='Remarks')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    @api.model
    def create_checklist_for_vendor(self, vendor_id, vendor_type):
        """Create checklist items for a vendor based on vendor type"""
        vendor = self.env['vendor.vendor'].browse(vendor_id)
        templates = self.env['vendor.checklist.template'].search([
            '|', ('vendor_type', '=', vendor_type), ('vendor_type', '=', False)
        ])

        checklist_items = []
        for template in templates:
            checklist_items.append((0, 0, {
                'vendor_id': vendor_id,
                'checklist_template_id': template.id,
            }))

        if checklist_items:
            vendor.write({'checklist_ids': checklist_items})

    def action_mark_complete(self):
        self.write({
            'completed': True,
            'completed_by_id': self.env.user.id,
            'completed_date': fields.Date.today()
        })


class VendorChecklistTemplate(models.Model):
    _name = 'vendor.checklist.template'
    _description = 'Vendor Checklist Template'
    _order = 'sequence, id'

    name = fields.Char(string='Checklist Item', required=True)
    description = fields.Text(string='Description')
    category = fields.Selection([
        ('documentation', 'Documentation'),
        ('financial', 'Financial'),
        ('technical', 'Technical Capability'),
        ('quality', 'Quality Standards'),
        ('compliance', 'Legal & Compliance'),
        ('safety', 'Safety & Environment'),
        ('references', 'References')
    ], string='Category', required=True)

    vendor_type = fields.Selection([
        ('goods', 'Goods Supplier'),
        ('services', 'Service Provider'),
        ('both', 'Goods & Services'),
        ('contractor', 'Contractor'),
        ('consultant', 'Consultant'),
        ('machining', 'Machining'),
        ('fabrication', 'Fabrication'),
        ('casting', 'Casting'),
        ('raw_material', 'Raw Material'),
        ('maintenance', 'Maintenance')
    ], string='Applicable for Vendor Type', help='Leave empty for all types')

    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    mandatory = fields.Boolean(string='Mandatory', default=True)
    requires_document = fields.Boolean(string='Requires Document Upload', default=False)
