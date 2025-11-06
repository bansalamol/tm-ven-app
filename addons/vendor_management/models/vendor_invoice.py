# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class VendorInvoice(models.Model):
    _name = 'vendor.invoice'
    _description = 'Vendor Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_invoice desc'

    name = fields.Char(string='Invoice Number', required=True, tracking=True)
    vendor_invoice_number = fields.Char(string='Vendor Invoice No.', required=True, tracking=True)

    vendor_id = fields.Many2one('vendor.vendor', string='Vendor', required=True, tracking=True, index=True)
    po_id = fields.Many2one('vendor.purchase.order', string='Purchase Order', tracking=True)
    grn_id = fields.Many2one('vendor.grn', string='GRN', tracking=True)

    date_invoice = fields.Date(string='Invoice Date', required=True, tracking=True)
    date_due = fields.Date(string='Due Date', required=True, tracking=True)
    date_received = fields.Date(string='Received Date', default=fields.Date.today)

    line_ids = fields.One2many('vendor.invoice.line', 'invoice_id', string='Invoice Lines')

    amount_untaxed = fields.Monetary(string='Untaxed Amount', compute='_compute_amounts', store=True)
    amount_tax = fields.Monetary(string='Tax Amount', compute='_compute_amounts', store=True)
    amount_total = fields.Monetary(string='Total Amount', compute='_compute_amounts', store=True)
    amount_paid = fields.Monetary(string='Paid Amount', compute='_compute_amount_paid', store=True)
    amount_due = fields.Monetary(string='Due Amount', compute='_compute_amount_paid', store=True)

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    payment_term_id = fields.Many2one(related='vendor_id.payment_term_id', string='Payment Terms')

    payment_ids = fields.One2many('vendor.payment', 'invoice_id', string='Payments')
    payment_count = fields.Integer(string='Payment Count', compute='_compute_payment_count')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)

    verified_by_id = fields.Many2one('res.users', string='Verified By', tracking=True)
    approved_by_id = fields.Many2one('res.users', string='Approved By', tracking=True)

    notes = fields.Text(string='Notes')
    rejection_reason = fields.Text(string='Rejection Reason')

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    @api.depends('line_ids', 'line_ids.price_subtotal', 'line_ids.price_tax')
    def _compute_amounts(self):
        for invoice in self:
            amount_untaxed = amount_tax = 0.0
            for line in invoice.line_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            invoice.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('payment_ids', 'payment_ids.amount', 'payment_ids.state')
    def _compute_amount_paid(self):
        for invoice in self:
            paid_amount = sum(
                invoice.payment_ids.filtered(lambda p: p.state == 'paid').mapped('amount')
            )
            invoice.amount_paid = paid_amount
            invoice.amount_due = invoice.amount_total - paid_amount

    def _compute_payment_count(self):
        for invoice in self:
            invoice.payment_count = len(invoice.payment_ids)

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_verify(self):
        self.write({
            'state': 'verified',
            'verified_by_id': self.env.user.id
        })

    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by_id': self.env.user.id
        })

    def action_reject(self):
        return {
            'name': _('Reject Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.invoice.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_invoice_id': self.id},
        }

    def action_create_payment(self):
        return {
            'name': _('Register Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.payment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_invoice_id': self.id,
                'default_vendor_id': self.vendor_id.id,
                'default_amount': self.amount_due
            },
        }

    def action_view_payments(self):
        self.ensure_one()
        return {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.payment',
            'view_mode': 'tree,form',
            'domain': [('invoice_id', '=', self.id)],
        }


class VendorInvoiceLine(models.Model):
    _name = 'vendor.invoice.line'
    _description = 'Vendor Invoice Line'

    invoice_id = fields.Many2one('vendor.invoice', string='Invoice', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Text(string='Description')

    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    uom_id = fields.Many2one('uom.uom', string='UoM', required=True)

    unit_price = fields.Float(string='Unit Price', required=True)
    tax_ids = fields.Many2many('account.tax', string='Taxes')

    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_amount', store=True)
    price_tax = fields.Monetary(string='Tax', compute='_compute_amount', store=True)
    price_total = fields.Monetary(string='Total', compute='_compute_amount', store=True)

    currency_id = fields.Many2one(related='invoice_id.currency_id', string='Currency')

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
