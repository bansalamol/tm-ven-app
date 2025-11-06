#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation Script for Vendor Management Module
Checks for implementation gaps and errors
"""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

class ModuleValidator:
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.errors = []
        self.warnings = []
        self.info = []

    def validate_all(self):
        """Run all validation checks"""
        print("=" * 80)
        print("VENDOR MANAGEMENT MODULE VALIDATION")
        print("=" * 80)

        self.check_models()
        self.check_security()
        self.check_views()
        self.check_manifest()
        self.check_sequences()
        self.check_menus()

        self.print_report()

    def check_models(self):
        """Validate all model files"""
        print("\n[1/6] Checking Models...")

        models_init = self.module_path / 'models' / '__init__.py'
        if not models_init.exists():
            self.errors.append("models/__init__.py not found")
            return

        with open(models_init) as f:
            imports = f.read()

        # Expected models
        expected_models = [
            'vendor_category', 'vendor_rating', 'vendor', 'vendor_document',
            'vendor_checklist', 'vendor_rfq', 'vendor_quotation',
            'vendor_purchase_order', 'vendor_ncr', 'vendor_grn',
            'vendor_invoice', 'vendor_payment', 'wizards'
        ]

        for model in expected_models:
            if f'from . import {model}' not in imports:
                self.errors.append(f"Model '{model}' not imported in __init__.py")
            else:
                # Check if file exists
                model_file = self.module_path / 'models' / f'{model}.py'
                if not model_file.exists():
                    self.errors.append(f"Model file '{model}.py' not found")
                else:
                    self.info.append(f"✓ Model {model}.py exists and imported")

        print(f"  Models checked: {len(expected_models)}")

    def check_security(self):
        """Validate security access rights"""
        print("\n[2/6] Checking Security...")

        access_file = self.module_path / 'security' / 'ir.model.access.csv'
        security_file = self.module_path / 'security' / 'vendor_management_security.xml'

        if not access_file.exists():
            self.errors.append("ir.model.access.csv not found")
            return

        with open(access_file) as f:
            content = f.read()

        # Expected models in security
        expected_access = [
            'model_vendor_vendor', 'model_vendor_category', 'model_vendor_rating',
            'model_vendor_tag', 'model_vendor_bank_account', 'model_vendor_document',
            'model_vendor_checklist', 'model_vendor_checklist_template',
            'model_vendor_rfq', 'model_vendor_rfq_line', 'model_vendor_quotation',
            'model_vendor_quotation_line', 'model_vendor_purchase_order',
            'model_vendor_purchase_order_line', 'model_vendor_ncr', 'model_vendor_grn',
            'model_vendor_grn_line', 'model_vendor_inspection_report',
            'model_vendor_invoice', 'model_vendor_invoice_line', 'model_vendor_payment',
            'model_vendor_ledger'
        ]

        for model in expected_access:
            if model not in content:
                self.warnings.append(f"Access rights for '{model}' not found in CSV")
            else:
                # Check if both user and manager access exists
                if f'{model},group_vendor_user' in content and f'{model},group_vendor_manager' in content:
                    self.info.append(f"✓ Access rights OK for {model}")
                else:
                    self.warnings.append(f"Incomplete access rights for {model}")

        print(f"  Models with access rights: {content.count('model_vendor')}")

    def check_views(self):
        """Validate all view files"""
        print("\n[3/6] Checking Views...")

        views_dir = self.module_path / 'views'
        if not views_dir.exists():
            self.errors.append("views directory not found")
            return

        view_files = list(views_dir.glob('*.xml'))
        print(f"  Found {len(view_files)} view files")

        for view_file in view_files:
            try:
                tree = ET.parse(view_file)
                root = tree.getroot()

                # Count views
                records = root.findall(".//record[@model='ir.ui.view']")
                actions = root.findall(".//record[@model='ir.actions.act_window']")
                menus = root.findall(".//menuitem")

                self.info.append(f"✓ {view_file.name}: {len(records)} views, {len(actions)} actions, {len(menus)} menus")

            except ET.ParseError as e:
                self.errors.append(f"XML parse error in {view_file.name}: {e}")

    def check_manifest(self):
        """Validate manifest file"""
        print("\n[4/6] Checking Manifest...")

        manifest = self.module_path / '__manifest__.py'
        if not manifest.exists():
            self.errors.append("__manifest__.py not found")
            return

        with open(manifest) as f:
            content = f.read()

        # Check dependencies
        required_deps = ['base', 'mail', 'contacts', 'product', 'uom', 'account', 'hr', 'portal']
        for dep in required_deps:
            if f"'{dep}'" in content:
                self.info.append(f"✓ Dependency '{dep}' declared")
            else:
                self.warnings.append(f"Dependency '{dep}' not declared")

        # Check data files
        expected_files = [
            'security/vendor_management_security.xml',
            'security/ir.model.access.csv',
            'data/vendor_sequences.xml',
            'data/vendor_category_data.xml',
            'data/vendor_checklist_data.xml',
            'views/vendor_rfq_views.xml',
            'views/vendor_quotation_views.xml',
            'views/vendor_po_views.xml',
            'views/vendor_grn_ncr_views.xml',
            'views/vendor_invoice_payment_views.xml',
            'views/vendor_document_checklist_views.xml',
        ]

        for file_path in expected_files:
            if file_path in content:
                # Check if file actually exists
                actual_file = self.module_path / file_path
                if actual_file.exists():
                    self.info.append(f"✓ Data file '{file_path}' declared and exists")
                else:
                    self.errors.append(f"Data file '{file_path}' declared but missing")
            else:
                self.warnings.append(f"Data file '{file_path}' not declared in manifest")

    def check_sequences(self):
        """Validate sequences"""
        print("\n[5/6] Checking Sequences...")

        seq_file = self.module_path / 'data' / 'vendor_sequences.xml'
        if not seq_file.exists():
            self.errors.append("vendor_sequences.xml not found")
            return

        try:
            tree = ET.parse(seq_file)
            sequences = tree.findall(".//record[@model='ir.sequence']")

            expected_sequences = [
                'seq_vendor_vendor', 'seq_vendor_rfq', 'seq_vendor_purchase_order',
                'seq_vendor_grn', 'seq_vendor_ncr', 'seq_vendor_inspection_report',
                'seq_vendor_payment'
            ]

            for seq in expected_sequences:
                seq_found = any(s.get('id') == seq for s in sequences)
                if seq_found:
                    self.info.append(f"✓ Sequence '{seq}' defined")
                else:
                    self.warnings.append(f"Sequence '{seq}' not found")

            print(f"  Sequences defined: {len(sequences)}")

        except ET.ParseError as e:
            self.errors.append(f"XML parse error in sequences: {e}")

    def check_menus(self):
        """Validate menu structure"""
        print("\n[6/6] Checking Menus...")

        menu_files = [
            self.module_path / 'views' / 'vendor_menus.xml',
            self.module_path / 'views' / 'vendor_menus_extended.xml'
        ]

        total_menus = 0
        for menu_file in menu_files:
            if menu_file.exists():
                try:
                    tree = ET.parse(menu_file)
                    menus = tree.findall(".//menuitem")
                    total_menus += len(menus)
                    self.info.append(f"✓ {menu_file.name}: {len(menus)} menu items")
                except ET.ParseError as e:
                    self.errors.append(f"XML parse error in {menu_file.name}: {e}")
            else:
                self.warnings.append(f"Menu file {menu_file.name} not found")

        print(f"  Total menu items: {total_menus}")

    def print_report(self):
        """Print validation report"""
        print("\n" + "=" * 80)
        print("VALIDATION REPORT")
        print("=" * 80)

        print(f"\n✅ INFO ({len(self.info)}):")
        for msg in self.info[:10]:  # Show first 10
            print(f"  {msg}")
        if len(self.info) > 10:
            print(f"  ... and {len(self.info) - 10} more")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for msg in self.warnings:
                print(f"  {msg}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for msg in self.errors:
                print(f"  {msg}")

        print("\n" + "=" * 80)
        if self.errors:
            print("STATUS: ❌ VALIDATION FAILED - Fix errors before deployment")
        elif self.warnings:
            print("STATUS: ⚠️  VALIDATION PASSED WITH WARNINGS")
        else:
            print("STATUS: ✅ VALIDATION PASSED - 100% Complete!")
        print("=" * 80)

        return len(self.errors) == 0

if __name__ == '__main__':
    validator = ModuleValidator('/home/user/tm-ven-app/addons/vendor_management')
    success = validator.validate_all()
    exit(0 if success else 1)
