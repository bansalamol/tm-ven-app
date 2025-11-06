# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VendorPayment(models.Model):
    _name = 'vendor.payment'
    _description = 'Vendor Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'payment_date desc'

    name = fields.Char(string='Payment Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    vendor_id = fields.Many2one('vendor.vendor', string='Vendor', required=True, tracking=True, index=True)
    invoice_id = fields.Many2one('vendor.invoice', string='Invoice', tracking=True)

    payment_date = fields.Date(string='Payment Date', default=fields.Date.today, required=True, tracking=True)
    amount = fields.Monetary(string='Amount', required=True, tracking=True)

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer'),
        ('neft', 'NEFT'),
        ('rtgs', 'RTGS'),
        ('online', 'Online Payment'),
        ('other', 'Other')
    ], string='Payment Method', required=True, tracking=True)

    payment_reference = fields.Char(string='Transaction Reference', help='Cheque number, transaction ID, etc.')
    bank_account_id = fields.Many2one('vendor.bank.account', string='Vendor Bank Account')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)

    approved_by_id = fields.Many2one('res.users', string='Approved By', tracking=True)
    approved_date = fields.Date(string='Approval Date')

    notes = fields.Text(string='Notes')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Payment reference must be unique!'),
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('vendor.payment') or _('New')
        return super(VendorPayment, self).create(vals)

    @api.constrains('amount', 'invoice_id')
    def _check_amount(self):
        for payment in self:
            if payment.invoice_id and payment.amount > payment.invoice_id.amount_due:
                raise ValidationError(_('Payment amount cannot exceed invoice due amount.'))

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by_id': self.env.user.id,
            'approved_date': fields.Date.today()
        })

    def action_mark_paid(self):
        self.write({'state': 'paid'})
        # Update invoice state if fully paid
        if self.invoice_id:
            if self.invoice_id.amount_due <= 0:
                self.invoice_id.write({'state': 'paid'})
            # Update PO state
            if self.invoice_id.po_id:
                all_invoices_paid = all(
                    inv.state == 'paid' for inv in self.invoice_id.po_id.invoice_ids
                )
                if all_invoices_paid:
                    self.invoice_id.po_id.write({'state': 'paid'})

        # Update vendor statistics
        self.vendor_id.write({
            'pending_payment': self.vendor_id.pending_payment - self.amount
        })

        # Send payment advice email
        if self.vendor_id.email:
            self.vendor_id.message_post(
                body=_('Payment of %s %s has been processed for invoice %s') % (
                    self.amount, self.currency_id.name, self.invoice_id.name or ''
                ),
                subject=_('Payment Advice: %s') % self.name
            )

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class VendorLedger(models.Model):
    _name = 'vendor.ledger'
    _description = 'Vendor Ledger'
    _order = 'date desc'

    vendor_id = fields.Many2one('vendor.vendor', string='Vendor', required=True, index=True)
    date = fields.Date(string='Date', required=True, index=True)

    transaction_type = fields.Selection([
        ('invoice', 'Invoice'),
        ('payment', 'Payment'),
        ('debit_note', 'Debit Note'),
        ('credit_note', 'Credit Note'),
        ('adjustment', 'Adjustment')
    ], string='Transaction Type', required=True)

    reference = fields.Char(string='Reference')
    description = fields.Text(string='Description')

    debit = fields.Monetary(string='Debit')
    credit = fields.Monetary(string='Credit')
    balance = fields.Monetary(string='Balance', compute='_compute_balance', store=True)

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.depends('debit', 'credit')
    def _compute_balance(self):
        for ledger in self:
            previous_balance = self.search([
                ('vendor_id', '=', ledger.vendor_id.id),
                ('date', '<', ledger.date),
                ('id', '<', ledger.id)
            ], limit=1, order='date desc, id desc')

            prev_bal = previous_balance.balance if previous_balance else 0.0
            ledger.balance = prev_bal + ledger.debit - ledger.credit
