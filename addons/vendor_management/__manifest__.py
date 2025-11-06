# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Vendor Management',
    'version': '1.0',
    'sequence': 95,
    'category': 'Operations/Vendor Management',
    'summary': 'Manage vendors, supplier relationships, ratings and evaluations',
    'description': """
Enterprise Vendor Management System
===================================
Comprehensive vendor management solution for Odoo 19 with complete procurement workflow:

Core Features
------------
* Vendor Registration & Onboarding with approval workflow
* Document Management (GST, PAN, ISO, certifications)
* Pre-qualification Checklist System
* Auto-generated vendor codes and classification

Procurement Management
---------------------
* Request for Quotation (RFQ) creation and broadcasting
* Vendor quotation submission and comparison
* Technical and commercial evaluation
* Purchase Order (PO) management

Quality & Compliance
-------------------
* Quality ratings and performance tracking
* Non-Conformance Report (NCR) tracking
* Goods Receipt Note (GRN) with inspection
* Certificate management with expiry alerts

Financial Management
-------------------
* Invoice submission and verification workflow
* Payment tracking and approval
* Vendor ledger and outstanding balance
* Credit limit management

Advanced Features
----------------
* KPI-based vendor performance evaluation
* Multi-company and multi-currency support
* Role-based access control
* Automated notifications and alerts
* Comprehensive reporting and dashboards
    """,
    'depends': [
        'base',
        'mail',
        'contacts',
        'product',
        'uom',
        'account',
        'hr',
        'portal',
    ],
    'data': [
        # Security
        'security/vendor_management_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/vendor_sequences.xml',
        'data/vendor_category_data.xml',
        'data/vendor_checklist_data.xml',

        # Views - Core
        'views/vendor_category_views.xml',
        'views/vendor_rating_views.xml',
        'views/vendor_views.xml',

        # Views - Procurement
        'views/vendor_rfq_views.xml',
        'views/vendor_quotation_views.xml',
        'views/vendor_po_views.xml',

        # Views - Quality
        'views/vendor_grn_ncr_views.xml',

        # Views - Financial
        'views/vendor_invoice_payment_views.xml',

        # Views - Documents & Checklist
        'views/vendor_document_checklist_views.xml',

        # Views - Extended Features
        'views/vendor_views_extended.xml',
        'views/vendor_wizard_views.xml',

        # Menus
        'views/vendor_menus.xml',
        'views/vendor_menus_extended.xml',
    ],
    'demo': [
        'data/vendor_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'vendor_management/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
}
