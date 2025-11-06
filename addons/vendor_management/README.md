# Vendor Management Module for Odoo 19

A comprehensive vendor management system for Odoo 19 that helps you manage suppliers, track ratings, and maintain vendor relationships.

## Features

### Vendor Management
- Complete vendor master data with contact information
- Address management with country and state support
- Multiple bank accounts per vendor
- Document and certificate storage
- Multi-company support

### Vendor Classification
- Hierarchical vendor categories
- Vendor types: Goods Supplier, Service Provider, Contractor, Consultant
- Flexible tagging system with color coding
- Vendor status tracking: Active, On Hold, Blocked, Potential

### Rating & Evaluation System
- Multi-criteria rating system:
  - Quality Rating
  - Delivery Rating
  - Service Rating
  - Pricing Rating
- Automatic overall rating calculation
- Rating history tracking
- Average rating computation per vendor

### Business Information
- VAT and Tax ID tracking
- Registration number management
- Payment terms configuration
- Currency support
- Banking details management

### User Interface
- Modern Kanban view for quick overview
- Comprehensive form view with tabs
- Advanced search and filtering
- Statistics and reporting
- Mobile-responsive design

### Security
- Two-level access control:
  - **User**: Can view and create vendors and ratings
  - **Manager**: Full access to all vendor management features
- Multi-company security rules
- Record-level access control

## Installation

1. Copy the `vendor_management` folder to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "Vendor Management" module

## Configuration

1. Go to **Vendor Management > Configuration > Vendor Categories**
2. Create or customize vendor categories
3. Set up user permissions in **Settings > Users & Companies > Groups**

## Usage

### Creating a Vendor
1. Go to **Vendor Management > Vendors**
2. Click **Create**
3. Fill in vendor information across the tabs:
   - Basic Information
   - Contact Information
   - Business Information
   - Bank Accounts
4. Save the vendor

### Rating a Vendor
1. Open a vendor record
2. Click on the **Ratings** button or go to the Ratings tab
3. Create a new rating
4. Fill in the rating criteria
5. Confirm the rating

### Managing Categories
1. Go to **Vendor Management > Configuration > Vendor Categories**
2. Create categories with parent-child relationships
3. Assign colors for visual identification

## Technical Details

- **Odoo Version**: 19.0
- **Dependencies**: base, mail, contacts
- **License**: LGPL-3
- **Models**:
  - `vendor.vendor`: Main vendor entity
  - `vendor.category`: Vendor categorization
  - `vendor.rating`: Vendor performance ratings
  - `vendor.tag`: Vendor tags for classification
  - `vendor.bank.account`: Bank account details

## Author

Custom Odoo Development

## Support

For issues, questions, or contributions, please contact your system administrator.
