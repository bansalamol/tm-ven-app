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
        ('consultant', 'Consultant'),
        ('machining', 'Machining'),
        ('fabrication', 'Fabrication'),
        ('casting', 'Casting'),
        ('raw_material', 'Raw Material'),
        ('maintenance', 'Maintenance')
    ], string='Vendor Type', default='goods', required=True, tracking=True)

    vendor_classification = fields.Selection([
        ('a', 'A - Premium'),
        ('b', 'B - Standard'),
        ('c', 'C - Basic')
    ], string='Vendor Classification', tracking=True, compute='_compute_vendor_classification', store=True)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('blocked', 'Blocked'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', required=True, tracking=True)

    onboarding_state = fields.Selection([
        ('new', 'New Registration'),
        ('document_pending', 'Documents Pending'),
        ('under_review', 'Under Review'),
        ('qualified', 'Qualified'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Onboarding Status', default='new', tracking=True)

    # Rating Information
    rating_ids = fields.One2many('vendor.rating', 'vendor_id', string='Ratings')
    average_rating = fields.Float(string='Average Rating', compute='_compute_average_rating', store=True)
    rating_count = fields.Integer(string='Rating Count', compute='_compute_rating_count')

    # Compliance & Documents
    document_ids = fields.One2many('vendor.document', 'vendor_id', string='Documents')
    gst_number = fields.Char(string='GST Number', tracking=True)
    pan_number = fields.Char(string='PAN Number', tracking=True)
    iso_certified = fields.Boolean(string='ISO Certified', tracking=True)
    iso_certificate_number = fields.Char(string='ISO Certificate Number')
    iso_valid_until = fields.Date(string='ISO Valid Until')

    # Capabilities
    capabilities = fields.Text(string='Capabilities/Products Supplied')
    production_capacity = fields.Char(string='Production Capacity')
    lead_time_days = fields.Integer(string='Standard Lead Time (Days)')

    # Quality Metrics
    quality_score = fields.Float(string='Quality Score', compute='_compute_quality_metrics', store=True)
    delivery_score = fields.Float(string='Delivery Score', compute='_compute_quality_metrics', store=True)
    rejection_rate = fields.Float(string='Rejection Rate %', readonly=True)
    ncr_count = fields.Integer(string='NCR Count', compute='_compute_ncr_count')

    # Onboarding & Approval
    checklist_ids = fields.One2many('vendor.checklist', 'vendor_id', string='Pre-qualification Checklist')
    checklist_completed = fields.Boolean(string='Checklist Completed', compute='_compute_checklist_completed')
    approved_by_id = fields.Many2one('res.users', string='Approved By', tracking=True)
    approved_date = fields.Date(string='Approval Date', tracking=True)
    rejection_reason = fields.Text(string='Rejection Reason')

    # Portal Access
    portal_user_id = fields.Many2one('res.users', string='Portal User', domain=[('share', '=', True)])

    # Additional Information
    notes = fields.Text(string='Notes')
    internal_notes = fields.Text(string='Internal Notes')
    date_joined = fields.Date(string='Date Joined', default=fields.Date.today, tracking=True)
    last_purchase_date = fields.Date(string='Last Purchase Date', readonly=True)

    # Statistics
    total_purchases = fields.Float(string='Total Purchases', readonly=True)
    purchase_count = fields.Integer(string='Purchase Count', readonly=True)
    rfq_count = fields.Integer(string='RFQ Count', compute='_compute_rfq_count')
    po_count = fields.Integer(string='PO Count', compute='_compute_po_count')
    pending_payment = fields.Float(string='Pending Payment', readonly=True)
    credit_limit = fields.Float(string='Credit Limit')

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Vendor code must be unique!'),
    ]

    @api.depends('average_rating', 'purchase_count', 'total_purchases')
    def _compute_vendor_classification(self):
        for vendor in self:
            # Auto-classify based on rating, purchase volume
            if vendor.average_rating >= 4.5 and vendor.total_purchases > 500000:
                vendor.vendor_classification = 'a'
            elif vendor.average_rating >= 3.5 and vendor.total_purchases > 100000:
                vendor.vendor_classification = 'b'
            else:
                vendor.vendor_classification = 'c'

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

    @api.depends('rating_ids', 'rating_ids.quality_rating', 'rating_ids.delivery_rating', 'rating_ids.state')
    def _compute_quality_metrics(self):
        for vendor in self:
            confirmed_ratings = vendor.rating_ids.filtered(lambda r: r.state == 'confirmed')
            if confirmed_ratings:
                quality_scores = [float(r.quality_rating) for r in confirmed_ratings if r.quality_rating]
                delivery_scores = [float(r.delivery_rating) for r in confirmed_ratings if r.delivery_rating]
                vendor.quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
                vendor.delivery_score = sum(delivery_scores) / len(delivery_scores) if delivery_scores else 0.0
            else:
                vendor.quality_score = 0.0
                vendor.delivery_score = 0.0

    def _compute_ncr_count(self):
        ncr_obj = self.env['vendor.ncr']
        for vendor in self:
            vendor.ncr_count = ncr_obj.search_count([('vendor_id', '=', vendor.id)])

    def _compute_rfq_count(self):
        rfq_obj = self.env['vendor.rfq']
        for vendor in self:
            vendor.rfq_count = rfq_obj.search_count([('vendor_ids', 'in', vendor.id)])

    def _compute_po_count(self):
        po_obj = self.env['vendor.purchase.order']
        for vendor in self:
            vendor.po_count = po_obj.search_count([('vendor_id', '=', vendor.id)])

    @api.depends('checklist_ids', 'checklist_ids.completed')
    def _compute_checklist_completed(self):
        for vendor in self:
            if vendor.checklist_ids:
                vendor.checklist_completed = all(item.completed for item in vendor.checklist_ids)
            else:
                vendor.checklist_completed = False

    @api.constrains('email')
    def _check_email(self):
        for vendor in self:
            if vendor.email and '@' not in vendor.email:
                raise ValidationError(_('Please enter a valid email address.'))

    @api.model
    def create(self, vals):
        # Auto-generate vendor code if not provided
        if not vals.get('code'):
            sequence = self.env['ir.sequence'].next_by_code('vendor.vendor') or 'VEN000'
            vals['code'] = sequence
        return super(Vendor, self).create(vals)

    def action_submit_for_approval(self):
        self.write({
            'status': 'pending_approval',
            'onboarding_state': 'under_review'
        })

    def action_approve(self):
        self.write({
            'status': 'approved',
            'onboarding_state': 'approved',
            'approved_by_id': self.env.user.id,
            'approved_date': fields.Date.today()
        })

    def action_reject(self):
        return {
            'name': _('Reject Vendor'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_vendor_id': self.id},
        }

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

    def action_view_documents(self):
        self.ensure_one()
        return {
            'name': _('Vendor Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.document',
            'view_mode': 'tree,form',
            'domain': [('vendor_id', '=', self.id)],
            'context': {'default_vendor_id': self.id},
        }

    def action_view_rfqs(self):
        self.ensure_one()
        return {
            'name': _('RFQs'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.rfq',
            'view_mode': 'tree,form',
            'domain': [('vendor_ids', 'in', self.id)],
        }

    def action_view_pos(self):
        self.ensure_one()
        return {
            'name': _('Purchase Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.purchase.order',
            'view_mode': 'tree,form',
            'domain': [('vendor_id', '=', self.id)],
            'context': {'default_vendor_id': self.id},
        }

    def action_view_ncrs(self):
        self.ensure_one()
        return {
            'name': _('Non-Conformance Reports'),
            'type': 'ir.actions.act_window',
            'res_model': 'vendor.ncr',
            'view_mode': 'tree,form',
            'domain': [('vendor_id', '=', self.id)],
            'context': {'default_vendor_id': self.id},
        }

    def check_certificate_expiry(self):
        """Automated action to check certificate expiry and send alerts"""
        today = fields.Date.today()
        vendors = self.search([
            ('iso_certified', '=', True),
            ('iso_valid_until', '!=', False),
            ('iso_valid_until', '<=', fields.Date.add(today, days=30))
        ])
        for vendor in vendors:
            # Send notification
            vendor.message_post(
                body=_('ISO certificate expiring on %s. Please renew.') % vendor.iso_valid_until,
                subject=_('Certificate Expiry Alert')
            )


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
