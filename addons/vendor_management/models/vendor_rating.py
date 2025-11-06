# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VendorRating(models.Model):
    _name = 'vendor.rating'
    _description = 'Vendor Rating'
    _order = 'rating_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    vendor_id = fields.Many2one('vendor.vendor', string='Vendor', required=True, ondelete='cascade', index=True)
    rating_date = fields.Date(string='Rating Date', required=True, default=fields.Date.today, tracking=True)
    rated_by_id = fields.Many2one('res.users', string='Rated By', default=lambda self: self.env.user, required=True)

    # Rating Criteria
    quality_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Below Average'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent')
    ], string='Quality Rating', required=True, tracking=True)

    delivery_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Below Average'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent')
    ], string='Delivery Rating', required=True, tracking=True)

    service_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Below Average'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent')
    ], string='Service Rating', required=True, tracking=True)

    pricing_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Below Average'),
        ('3', 'Average'),
        ('4', 'Good'),
        ('5', 'Excellent')
    ], string='Pricing Rating', required=True, tracking=True)

    overall_rating = fields.Float(string='Overall Rating', compute='_compute_overall_rating', store=True, tracking=True)
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)

    @api.depends('quality_rating', 'delivery_rating', 'service_rating', 'pricing_rating')
    def _compute_overall_rating(self):
        for rating in self:
            if rating.quality_rating and rating.delivery_rating and rating.service_rating and rating.pricing_rating:
                total = (int(rating.quality_rating) + int(rating.delivery_rating) +
                        int(rating.service_rating) + int(rating.pricing_rating))
                rating.overall_rating = total / 4.0
            else:
                rating.overall_rating = 0.0

    def action_confirm(self):
        self.write({'state': 'confirmed'})
        # Update vendor's average rating
        for rating in self:
            rating.vendor_id._compute_average_rating()

    def action_cancel(self):
        self.write({'state': 'cancelled'})
