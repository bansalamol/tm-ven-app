# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Vendor Management',
    'version': '1.0',
    'sequence': 95,
    'category': 'Operations/Vendor Management',
    'summary': 'Manage vendors, supplier relationships, ratings and evaluations',
    'description': """
Vendor Management System
========================
Comprehensive vendor management module for Odoo 19 that helps you:

Main Features
-------------
* Maintain vendor master data with complete contact information
* Categorize vendors by type and business area
* Track vendor ratings and performance evaluations
* Manage vendor status (active, blocked, on-hold)
* Store vendor documents and certificates
* Track payment terms and banking details
* Multi-company support
* Advanced search and filtering capabilities
    """,
    'depends': [
        'base',
        'mail',
        'contacts',
    ],
    'data': [
        'security/vendor_management_security.xml',
        'security/ir.model.access.csv',
        'views/vendor_category_views.xml',
        'views/vendor_rating_views.xml',
        'views/vendor_views.xml',
        'views/vendor_menus.xml',
        'data/vendor_category_data.xml',
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
