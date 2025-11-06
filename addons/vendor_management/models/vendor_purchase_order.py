# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class VendorPurchaseOrder(models.Model):
    _name = 'vendor.purchase.order'
    _description = 'Purchase Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_order desc'

    name = fields.Char(string='PO Number', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    vendor_id = fields.Many2one('vendor.vendor', string='Vendor', required=True, tracking=True, index=True)
    rfq_id = fields.Many2one('vendor.rfq', string='Source RFQ')
    quotation_id = fields.Many2one('vendor.quotation', string='Source Quotation')

    date_order = fields.Date(string='Order Date', default=fields.Date.today, required=True, tracking=True)
    date_planned = fields.Date(string='Expected Delivery Date', required=True, tracking=True)
    date_delivered = fields.Date(string='Actual Delivery Date', tracking=True)

    order_line_ids = fields.One2many('vendor.purchase.order.line', 'order_id', string='Order Lines')

    amount_untaxed = fields.Monetary(string='Untaxed Amount', compute='_compute_amounts', store=True)
    amount_tax = fields.Monetary(string='Tax Amount', compute='_compute_amounts', store=True)
    amount_total = fields.Monetary(string='Total Amount', compute='_compute_amounts', store=True)

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    payment_term_id = fields.Many2one(related='vendor_id.payment_term_id', string='Payment Terms')
    notes = fields.Text(string='Terms and Conditions')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent to Vendor'),
        ('confirmed', 'Confirmed'),
        ('received', 'Received'),
        ('invoiced', 'Invoiced'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)

    grn_ids = fields.One2many('vendor.grn', 'po_id', string='GRNs')
    grn_count = fields.Integer(string='GRN Count', compute='_compute_grn_count')

    invoice_ids = fields.One2many('vendor.invoice', 'po_id', string='Invoices')
    invoice_count = fields.Integer(string='Invoice Count', compute='_compute_invoice_count')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'PO number must be unique!'),
    ]

    @api.depends('order_line_ids', 'order_line_ids.price_subtotal', 'order_line_ids.price_tax')
    def _compute_amounts(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    def _compute_grn_count(self):
        for order in self:
            order.grn_count = len(order.grn_ids)

    def _compute_invoice_count(self):
        for order in self:
            order.invoice_count = len(order.invoice_ids)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('vendor.purchase.order') or _('New')
        return super(VendorPurchaseOrder, self).create(vals)

    def action_send_to_vendor(self):
        self.write({'state': 'sent'})
        # Send PO via email
        template = self.env.ref('vendor_management.email_template_po', raise_if_not_found=False)
        if template and self.vendor_id.email:
            template.send_mail(self.id, force_send=True)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_receive(self):
        return {
            'name': _('Create GRN'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.grn',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_po_id': self.id, 'default_vendor_id': self.vendor_id.id},
        }

    def action_view_grns(self):
        self.ensure_one()
        return {
            'name': _('Goods Receipt Notes'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.grn',
            'view_mode': 'tree,form',
            'domain': [('po_id', '=', self.id)],
        }

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'name': _('Vendor Invoices'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.invoice',
            'view_mode': 'tree,form',
            'domain': [('po_id', '=', self.id)],
        }

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class VendorPurchaseOrderLine(models.Model):
    _name = 'vendor.purchase.order.line'
    _description = 'Purchase Order Line'
    _order = 'sequence, id'

    order_id = fields.Many2one('vendor.purchase.order', string='Order', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)

    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Text(string='Description')

    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    qty_received = fields.Float(string='Received Qty', readonly=True)
    uom_id = fields.Many2one('uom.uom', string='UoM', required=True)

    unit_price = fields.Float(string='Unit Price', required=True)
    tax_ids = fields.Many2many('account.tax', string='Taxes')

    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_amount', store=True)
    price_tax = fields.Monetary(string='Tax', compute='_compute_amount', store=True)
    price_total = fields.Monetary(string='Total', compute='_compute_amount', store=True)

    currency_id = fields.Many2one(related='order_id.currency_id', string='Currency')

    @api.depends('quantity', 'unit_price', 'tax_ids')
    def _compute_amount(self):
        for line in self:
            price = line.unit_price * line.quantity
            if line.tax_ids:
                taxes = line.tax_ids.compute_all(line.unit_price, line.currency_id, line.quantity, line.product_id)
                line.update({
                    'price_subtotal': taxes['total_excluded'],
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'],
                })
            else:
                line.update({
                    'price_subtotal': price,
                    'price_tax': 0.0,
                    'price_total': price,
                })
