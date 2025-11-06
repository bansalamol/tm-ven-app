# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class VendorRFQ(models.Model):
    _name = 'vendor.rfq'
    _description = 'Request for Quotation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_created desc'

    name = fields.Char(string='RFQ Number', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    date_created = fields.Date(string='RFQ Date', default=fields.Date.today, required=True, tracking=True)
    deadline = fields.Date(string='Submission Deadline', required=True, tracking=True)

    vendor_ids = fields.Many2many('vendor.vendor', string='Invited Vendors', required=True, tracking=True)
    vendor_count = fields.Integer(string='Vendor Count', compute='_compute_vendor_count')

    line_ids = fields.One2many('vendor.rfq.line', 'rfq_id', string='RFQ Lines')
    quotation_ids = fields.One2many('vendor.quotation', 'rfq_id', string='Received Quotations')
    quotation_count = fields.Integer(string='Quotations Received', compute='_compute_quotation_count')

    category_id = fields.Many2one('vendor.category', string='Category')
    department_id = fields.Many2one('hr.department', string='Requesting Department')
    requested_by_id = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, tracking=True)

    description = fields.Text(string='Description')
    terms_conditions = fields.Text(string='Terms & Conditions')
    technical_specifications = fields.Text(string='Technical Specifications')

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', string='Currency')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent to Vendors'),
        ('quoted', 'Quotations Received'),
        ('evaluated', 'Under Evaluation'),
        ('awarded', 'Awarded'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)

    awarded_vendor_id = fields.Many2one('vendor.vendor', string='Awarded Vendor', tracking=True)
    awarded_quotation_id = fields.Many2one('vendor.quotation', string='Awarded Quotation', tracking=True)

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'RFQ number must be unique!'),
    ]

    @api.depends('vendor_ids')
    def _compute_vendor_count(self):
        for rfq in self:
            rfq.vendor_count = len(rfq.vendor_ids)

    @api.depends('quotation_ids')
    def _compute_quotation_count(self):
        for rfq in self:
            rfq.quotation_count = len(rfq.quotation_ids.filtered(lambda q: q.state != 'cancelled'))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('vendor.rfq') or _('New')
        return super(VendorRFQ, self).create(vals)

    def action_send_to_vendors(self):
        """Send RFQ to selected vendors via email"""
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_('Please add at least one item to the RFQ.'))

        self.write({'state': 'sent'})

        # Send email to all vendors
        template = self.env.ref('vendor_management.email_template_rfq', raise_if_not_found=False)
        for vendor in self.vendor_ids:
            if vendor.email and template:
                template.send_mail(self.id, force_send=True, email_values={
                    'email_to': vendor.email,
                    'subject': f'Request for Quotation - {self.name}'
                })
            # Create vendor quotation record
            self.env['vendor.quotation'].create({
                'rfq_id': self.id,
                'vendor_id': vendor.id,
                'state': 'draft'
            })

    def action_view_quotations(self):
        self.ensure_one()
        return {
            'name': _('Received Quotations'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.quotation',
            'view_mode': 'tree,form',
            'domain': [('rfq_id', '=', self.id)],
            'context': {'default_rfq_id': self.id},
        }

    def action_compare_quotations(self):
        self.ensure_one()
        return {
            'name': _('Compare Quotations'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.quotation.comparison.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_rfq_id': self.id},
        }

    def action_award(self, quotation_id):
        """Award RFQ to a specific quotation"""
        quotation = self.env['vendor.quotation'].browse(quotation_id)
        self.write({
            'state': 'awarded',
            'awarded_vendor_id': quotation.vendor_id.id,
            'awarded_quotation_id': quotation.id
        })
        quotation.write({'state': 'awarded'})

        # Mark other quotations as lost
        other_quotations = self.quotation_ids.filtered(lambda q: q.id != quotation_id)
        other_quotations.write({'state': 'lost'})

    def action_create_po(self):
        """Create Purchase Order from awarded quotation"""
        self.ensure_one()
        if not self.awarded_quotation_id:
            raise UserError(_('Please award the RFQ to a vendor first.'))

        po = self.env['vendor.purchase.order'].create({
            'vendor_id': self.awarded_vendor_id.id,
            'rfq_id': self.id,
            'quotation_id': self.awarded_quotation_id.id,
            'order_line_ids': [(0, 0, {
                'product_id': line.product_id.id,
                'description': line.description,
                'quantity': line.quantity,
                'uom_id': line.uom_id.id,
                'unit_price': q_line.unit_price,
                'tax_ids': [(6, 0, q_line.tax_ids.ids)],
            }) for line in self.line_ids for q_line in self.awarded_quotation_id.line_ids if q_line.rfq_line_id.id == line.id]
        })

        return {
            'name': _('Purchase Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.purchase.order',
            'res_id': po.id,
            'view_mode': 'form',
        }

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class VendorRFQLine(models.Model):
    _name = 'vendor.rfq.line'
    _description = 'RFQ Line'
    _order = 'sequence, id'

    rfq_id = fields.Many2one('vendor.rfq', string='RFQ', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)

    product_id = fields.Many2one('product.product', string='Product')
    description = fields.Text(string='Description', required=True)
    specifications = fields.Text(string='Technical Specifications')

    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)

    delivery_date_required = fields.Date(string='Required Delivery Date')
    notes = fields.Text(string='Notes')
