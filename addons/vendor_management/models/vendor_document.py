# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class VendorDocument(models.Model):
    _name = 'vendor.document'
    _description = 'Vendor Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'expiry_date asc'

    vendor_id = fields.Many2one('vendor.vendor', string='Vendor', required=True, ondelete='cascade', index=True)
    name = fields.Char(string='Document Name', required=True)
    document_type = fields.Selection([
        ('gst', 'GST Certificate'),
        ('pan', 'PAN Card'),
        ('iso', 'ISO Certification'),
        ('rohs', 'ROHS Certificate'),
        ('msme', 'MSME Certificate'),
        ('registration', 'Company Registration'),
        ('compliance', 'Compliance Document'),
        ('quality', 'Quality Certificate'),
        ('financial', 'Financial Document'),
        ('other', 'Other')
    ], string='Document Type', required=True, tracking=True)

    document_number = fields.Char(string='Document Number', tracking=True)
    issue_date = fields.Date(string='Issue Date', tracking=True)
    expiry_date = fields.Date(string='Expiry Date', tracking=True)
    is_expired = fields.Boolean(string='Expired', compute='_compute_is_expired', store=True)
    days_to_expiry = fields.Integer(string='Days to Expiry', compute='_compute_days_to_expiry')

    attachment_id = fields.Many2one('ir.attachment', string='Attachment', required=True, ondelete='cascade')
    file_name = fields.Char(related='attachment_id.name', string='File Name', readonly=True)
    file_size = fields.Integer(related='attachment_id.file_size', string='File Size', readonly=True)

    issuing_authority = fields.Char(string='Issuing Authority')
    notes = fields.Text(string='Notes')
    verified = fields.Boolean(string='Verified', tracking=True)
    verified_by_id = fields.Many2one('res.users', string='Verified By', tracking=True)
    verified_date = fields.Date(string='Verified Date', tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired')
    ], string='Status', default='draft', required=True, tracking=True)

    @api.depends('expiry_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for doc in self:
            if doc.expiry_date:
                doc.is_expired = doc.expiry_date < today
            else:
                doc.is_expired = False

    @api.depends('expiry_date')
    def _compute_days_to_expiry(self):
        today = fields.Date.today()
        for doc in self:
            if doc.expiry_date:
                delta = doc.expiry_date - today
                doc.days_to_expiry = delta.days
            else:
                doc.days_to_expiry = 0

    def action_verify(self):
        self.write({
            'verified': True,
            'verified_by_id': self.env.user.id,
            'verified_date': fields.Date.today(),
            'state': 'verified'
        })

    def action_reject(self):
        self.write({'state': 'rejected'})

    def check_document_expiry(self):
        """Cron job to check document expiry and send alerts"""
        today = fields.Date.today()
        alert_date = today + timedelta(days=30)

        expiring_docs = self.search([
            ('expiry_date', '!=', False),
            ('expiry_date', '<=', alert_date),
            ('expiry_date', '>=', today),
            ('state', 'in', ['verified', 'submitted'])
        ])

        for doc in expiring_docs:
            doc.vendor_id.message_post(
                body=_('%s (%s) expiring on %s. Please renew.') % (
                    doc.name, doc.document_type, doc.expiry_date
                ),
                subject=_('Document Expiry Alert'),
                subtype_xmlid='mail.mt_comment'
            )
            # Create activity
            doc.vendor_id.activity_schedule(
                'mail.mail_activity_data_warning',
                user_id=doc.vendor_id.create_uid.id or self.env.user.id,
                summary=_('Document Expiring: %s') % doc.name,
                note=_('Please renew %s before %s') % (doc.name, doc.expiry_date)
            )
