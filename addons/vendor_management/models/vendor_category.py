# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class VendorCategory(models.Model):
    _name = 'vendor.category'
    _description = 'Vendor Category'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True, translate=True)
    code = fields.Char(string='Category Code', required=True)
    parent_id = fields.Many2one('vendor.category', string='Parent Category', index=True, ondelete='cascade')
    child_ids = fields.One2many('vendor.category', 'parent_id', string='Child Categories')
    description = fields.Text(string='Description', translate=True)
    active = fields.Boolean(string='Active', default=True)
    color = fields.Integer(string='Color Index')
    vendor_count = fields.Integer(string='Vendor Count', compute='_compute_vendor_count')

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Category code must be unique!'),
    ]

    @api.depends('parent_id')
    def _compute_display_name(self):
        for category in self:
            if category.parent_id:
                category.display_name = f"{category.parent_id.name} / {category.name}"
            else:
                category.display_name = category.name

    def _compute_vendor_count(self):
        vendor_data = self.env['vendor.vendor'].read_group(
            [('category_id', 'in', self.ids)],
            ['category_id'],
            ['category_id']
        )
        mapped_data = {data['category_id'][0]: data['category_id_count'] for data in vendor_data}
        for category in self:
            category.vendor_count = mapped_data.get(category.id, 0)
