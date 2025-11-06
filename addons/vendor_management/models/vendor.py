# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Vendor(models.Model):
    _name = 'vendor.vendor'
    _description = 'Vendor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # Basic Information
    name = fields.Char(string='Vendor Name', required=True, tracking=True, index=True)
    code = fields.Char(string='Vendor Code', required=True, copy=False, tracking=True, index=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    category_id = fields.Many2one('vendor.category', string='Category', tracking=True, index=True)
    tag_ids = fields.Many2many('vendor.tag', string='Tags')

    # Contact Information
    contact_person = fields.Char(string='Contact Person', tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    mobile = fields.Char(string='Mobile', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    website = fields.Char(string='Website')

    # Address Information
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='ZIP Code')
    country_id = fields.Many2one('res.country', string='Country')

    # Business Information
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    vat = fields.Char(string='VAT Number', tracking=True)
    tax_id = fields.Char(string='Tax ID', tracking=True)
    registration_number = fields.Char(string='Registration Number', tracking=True)

    # Banking Details
    bank_ids = fields.One2many('vendor.bank.account', 'vendor_id', string='Bank Accounts')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Status and Classification
    vendor_type = fields.Selection([
        ('goods', 'Goods Supplier'),
        ('services', 'Service Provider'),
        ('both', 'Goods & Services'),
        ('contractor', 'Contractor'),
        ('consultant', 'Consultant')
    ], string='Vendor Type', default='goods', required=True, tracking=True)

    status = fields.Selection([
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('blocked', 'Blocked'),
        ('potential', 'Potential')
    ], string='Status', default='potential', required=True, tracking=True)

    # Rating Information
    rating_ids = fields.One2many('vendor.rating', 'vendor_id', string='Ratings')
    average_rating = fields.Float(string='Average Rating', compute='_compute_average_rating', store=True)
    rating_count = fields.Integer(string='Rating Count', compute='_compute_rating_count')

    # Additional Information
    notes = fields.Text(string='Notes')
    internal_notes = fields.Text(string='Internal Notes')
    date_joined = fields.Date(string='Date Joined', default=fields.Date.today, tracking=True)
    last_purchase_date = fields.Date(string='Last Purchase Date', readonly=True)

    # Statistics
    total_purchases = fields.Float(string='Total Purchases', readonly=True)
    purchase_count = fields.Integer(string='Purchase Count', readonly=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Vendor code must be unique!'),
    ]

    @api.depends('rating_ids', 'rating_ids.overall_rating', 'rating_ids.state')
    def _compute_average_rating(self):
        for vendor in self:
            confirmed_ratings = vendor.rating_ids.filtered(lambda r: r.state == 'confirmed')
            if confirmed_ratings:
                vendor.average_rating = sum(confirmed_ratings.mapped('overall_rating')) / len(confirmed_ratings)
            else:
                vendor.average_rating = 0.0

    @api.depends('rating_ids')
    def _compute_rating_count(self):
        for vendor in self:
            vendor.rating_count = len(vendor.rating_ids.filtered(lambda r: r.state == 'confirmed'))

    @api.constrains('email')
    def _check_email(self):
        for vendor in self:
            if vendor.email and '@' not in vendor.email:
                raise ValidationError(_('Please enter a valid email address.'))

    def action_set_active(self):
        self.write({'status': 'active'})

    def action_set_on_hold(self):
        self.write({'status': 'on_hold'})

    def action_set_blocked(self):
        self.write({'status': 'blocked'})

    def action_view_ratings(self):
        self.ensure_one()
        return {
            'name': _('Vendor Ratings'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.rating',
            'view_mode': 'tree,form',
            'domain': [('vendor_id', '=', self.id)],
            'context': {'default_vendor_id': self.id},
        }


class VendorTag(models.Model):
    _name = 'vendor.tag'
    _description = 'Vendor Tag'

    name = fields.Char(string='Tag Name', required=True, translate=True)
    color = fields.Integer(string='Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Tag name must be unique!'),
    ]


class VendorBankAccount(models.Model):
    _name = 'vendor.bank.account'
    _description = 'Vendor Bank Account'

    vendor_id = fields.Many2one('vendor.vendor', string='Vendor', required=True, ondelete='cascade')
    bank_name = fields.Char(string='Bank Name', required=True)
    account_number = fields.Char(string='Account Number', required=True)
    account_holder_name = fields.Char(string='Account Holder Name', required=True)
    bank_code = fields.Char(string='Bank Code/SWIFT')
    iban = fields.Char(string='IBAN')
    branch = fields.Char(string='Branch')
    is_primary = fields.Boolean(string='Primary Account', default=False)

    @api.constrains('is_primary')
    def _check_primary_account(self):
        for account in self:
            if account.is_primary:
                other_primary = self.search([
                    ('vendor_id', '=', account.vendor_id.id),
                    ('is_primary', '=', True),
                    ('id', '!=', account.id)
                ])
                if other_primary:
                    raise ValidationError(_('Only one primary bank account is allowed per vendor.'))
