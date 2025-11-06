# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class VendorRejectWizard(models.TransientModel):
    _name = 'vendor.reject.wizard'
    _description = 'Vendor Rejection Wizard'

    vendor_id = fields.Many2one('vendor.vendor', string='Vendor', required=True)
    rejection_reason = fields.Text(string='Rejection Reason', required=True)

    def action_reject(self):
        self.vendor_id.write({
            'status': 'rejected',
            'onboarding_state': 'rejected',
            'rejection_reason': self.rejection_reason
        })
        return {'type': 'ir.actions.act_window_close'}


class VendorInvoiceRejectWizard(models.TransientModel):
    _name = 'vendor.invoice.reject.wizard'
    _description = 'Invoice Rejection Wizard'

    invoice_id = fields.Many2one('vendor.invoice', string='Invoice', required=True)
    rejection_reason = fields.Text(string='Rejection Reason', required=True)

    def action_reject(self):
        self.invoice_id.write({
            'state': 'rejected',
            'rejection_reason': self.rejection_reason
        })
        # Notify vendor
        if self.invoice_id.vendor_id.email:
            self.invoice_id.vendor_id.message_post(
                body=_('Invoice %s has been rejected. Reason: %s') % (
                    self.invoice_id.name, self.rejection_reason
                ),
                subject=_('Invoice Rejected: %s') % self.invoice_id.name
            )
        return {'type': 'ir.actions.act_window_close'}


class VendorQuotationComparisonWizard(models.TransientModel):
    _name = 'vendor.quotation.comparison.wizard'
    _description = 'Quotation Comparison Wizard'

    rfq_id = fields.Many2one('vendor.rfq', string='RFQ', required=True)
    quotation_ids = fields.Many2many('vendor.quotation', string='Quotations to Compare',
                                      domain="[('rfq_id', '=', rfq_id), ('state', '=', 'submitted')]")
    comparison_line_ids = fields.One2many('vendor.quotation.comparison.line', 'wizard_id', string='Comparison Lines')

    @api.onchange('quotation_ids')
    def _onchange_quotation_ids(self):
        """Generate comparison lines when quotations are selected"""
        comparison_lines = []
        if self.quotation_ids and self.rfq_id:
            for rfq_line in self.rfq_id.line_ids:
                for quotation in self.quotation_ids:
                    q_line = quotation.line_ids.filtered(lambda l: l.rfq_line_id.id == rfq_line.id)
                    if q_line:
                        comparison_lines.append((0, 0, {
                            'rfq_line_id': rfq_line.id,
                            'quotation_id': quotation.id,
                            'vendor_id': quotation.vendor_id.id,
                            'unit_price': q_line.unit_price,
                            'subtotal': q_line.subtotal,
                            'delivery_lead_time': q_line.delivery_lead_time,
                        }))
        self.comparison_line_ids = comparison_lines

    def action_generate_report(self):
        """Generate comparison report"""
        return {
            'type': 'ir.actions.act_url',
            'url': f'/report/pdf/vendor_management.report_quotation_comparison/{self.id}',
            'target': 'new',
        }


class VendorQuotationComparisonLine(models.TransientModel):
    _name = 'vendor.quotation.comparison.line'
    _description = 'Quotation Comparison Line'

    wizard_id = fields.Many2one('vendor.quotation.comparison.wizard', string='Wizard', required=True, ondelete='cascade')
    rfq_line_id = fields.Many2one('vendor.rfq.line', string='RFQ Line', required=True)
    quotation_id = fields.Many2one('vendor.quotation', string='Quotation', required=True)
    vendor_id = fields.Many2one('vendor.vendor', string='Vendor', required=True)

    product_id = fields.Many2one(related='rfq_line_id.product_id', string='Product')
    description = fields.Text(related='rfq_line_id.description', string='Description')

    unit_price = fields.Float(string='Unit Price')
    subtotal = fields.Float(string='Subtotal')
    delivery_lead_time = fields.Integer(string='Lead Time (Days)')
