# 🚀 Deployment Guide - Vendor Management Module

**Module:** vendor_management v1.0
**Odoo Version:** 19.0
**Author:** Development Team
**Last Updated:** 2025-11-06

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Installing the Module (Test Environment)](#installing-the-module-test-environment)
4. [Testing & Validation](#testing--validation)
5. [Production Deployment](#production-deployment)
6. [Post-Deployment Configuration](#post-deployment-configuration)
7. [Troubleshooting](#troubleshooting)
8. [Backup & Rollback](#backup--rollback)

---

## Prerequisites

### System Requirements

**Server Requirements:**
- **OS:** Ubuntu 20.04 LTS or later / Debian 11+
- **RAM:** Minimum 4GB (8GB recommended for production)
- **Disk Space:** Minimum 10GB free space
- **Python:** Python 3.10 or later
- **PostgreSQL:** PostgreSQL 13 or later

**Odoo 19 Requirements:**
- Odoo 19 Community or Enterprise Edition
- All Odoo 19 dependencies installed
- PostgreSQL database configured

**Module Dependencies:**
```python
'depends': [
    'base',           # Odoo base module
    'mail',           # Chatter and messaging
    'contacts',       # Contact management
    'product',        # Product management
    'uom',            # Units of measure
    'account',        # Accounting (for currency)
    'hr',             # Human Resources (for users)
    'portal',         # Portal access
]
```

### Developer Tools (for testing)
- Git
- Text editor (VS Code, Sublime, etc.)
- Terminal/SSH access
- Database client (pgAdmin, DBeaver, etc.)

---

## Local Development Setup

### Step 1: Clone the Repository

```bash
# Navigate to your Odoo addons directory
cd /path/to/odoo/addons

# If using git repository
git clone <repository-url>
cd tm-ven-app

# Or copy the vendor_management folder directly
cp -r /path/to/vendor_management /path/to/odoo/addons/
```

### Step 2: Verify Module Files

```bash
cd /path/to/odoo/addons/vendor_management

# Check module structure
ls -la

# You should see:
# ├── __init__.py
# ├── __manifest__.py
# ├── models/
# ├── views/
# ├── security/
# ├── data/
# └── README.md
```

### Step 3: Set File Permissions

```bash
# Make sure Odoo user has read access
sudo chown -R odoo:odoo /path/to/odoo/addons/vendor_management
sudo chmod -R 755 /path/to/odoo/addons/vendor_management

# If running as current user (development)
chmod -R 755 /path/to/odoo/addons/vendor_management
```

### Step 4: Verify Dependencies

```bash
# Check if all dependent modules are available
cd /path/to/odoo/addons

# Base modules (should be in Odoo core)
ls -d base mail contacts product uom account hr portal

# If any missing, ensure Odoo is properly installed
```

### Step 5: Update Odoo Configuration

Edit your `odoo.conf` file:

```ini
[options]
# Add vendor_management addons path if not already included
addons_path = /path/to/odoo/addons,/path/to/vendor_management

# Development mode (for testing)
dev_mode = reload,qweb,werkzeug,xml

# Database configuration
db_host = localhost
db_port = 5432
db_user = odoo
db_password = <your-password>

# Log level for debugging
log_level = debug
log_handler = :DEBUG
```

### Step 6: Restart Odoo Server

```bash
# Stop Odoo
sudo systemctl stop odoo

# Or if running manually
pkill -f odoo-bin

# Start Odoo in development mode
/path/to/odoo/odoo-bin -c /path/to/odoo.conf --dev=all

# Or with systemd
sudo systemctl start odoo
```

---

## Installing the Module (Test Environment)

### Method 1: Web Interface (Recommended for Testing)

1. **Login to Odoo**
   ```
   URL: http://localhost:8069
   Database: <your-test-database>
   Login: admin
   ```

2. **Activate Developer Mode**
   - Click on Settings → Activate Developer Mode
   - Or append `?debug=1` to URL: `http://localhost:8069/web?debug=1`

3. **Update Apps List**
   - Go to: Apps → Update Apps List
   - Click "Update" button
   - Wait for completion

4. **Find the Module**
   - Search for "Vendor Management"
   - Click on the module card

5. **Install with Demo Data**
   - Check "Install demo data" option (recommended for testing)
   - Click "Install" button
   - Wait for installation (may take 1-2 minutes)

6. **Verify Installation**
   - Check top menu bar for "Vendor Management" menu
   - Go to: Vendor Management → Vendors → Vendors
   - You should see 5 demo vendors

### Method 2: Command Line Installation

```bash
# Install module with demo data
/path/to/odoo/odoo-bin -c /path/to/odoo.conf \
  -d <database-name> \
  -i vendor_management \
  --without-demo=False

# Install without demo data (production)
/path/to/odoo/odoo-bin -c /path/to/odoo.conf \
  -d <database-name> \
  -i vendor_management \
  --without-demo=all
```

### Method 3: Using Odoo Shell (Advanced)

```bash
# Start Odoo shell
/path/to/odoo/odoo-bin shell -c /path/to/odoo.conf -d <database-name>

# In the shell
>>> module = env['ir.module.module'].search([('name', '=', 'vendor_management')])
>>> module.button_immediate_install()
```

---

## Testing & Validation

### Automated Validation

Run the included validation script:

```bash
cd /path/to/odoo/addons/vendor_management

# Run validation
python3 validate_module.py

# Expected output:
# ✅ VALIDATION PASSED - 100% Complete!
# 76 checks passed, 0 errors, 0 warnings
```

### Manual Testing Checklist

#### 1. Module Installation (5 min)
- [ ] Module appears in Apps list
- [ ] Installation completes without errors
- [ ] "Vendor Management" menu appears in top menu
- [ ] All submenus are accessible

#### 2. Demo Data Verification (10 min)
- [ ] 5 vendors created (VEN00001 to VEN00005)
- [ ] Vendor categories visible (8 categories)
- [ ] Vendor tags working (4 tags)
- [ ] Documents attached to vendors
- [ ] Ratings visible for vendors

#### 3. Vendor Management (15 min)
- [ ] Can create new vendor
- [ ] Can upload documents
- [ ] Can complete checklist items
- [ ] Can rate vendor performance
- [ ] Vendor classification updates (A/B/C)
- [ ] Document expiry alerts work

#### 4. RFQ Workflow (20 min)
- [ ] Can create RFQ
- [ ] Can invite multiple vendors
- [ ] Can receive quotations
- [ ] Technical/commercial scoring works
- [ ] Overall score calculates correctly (60%/40%)
- [ ] Can award quotation

#### 5. Purchase Order Workflow (15 min)
- [ ] Can create PO from quotation
- [ ] PO links to RFQ and quotation
- [ ] State transitions work (draft → sent → confirmed)
- [ ] Can mark as received

#### 6. Quality Management (15 min)
- [ ] Can create GRN
- [ ] Inspection report creation works
- [ ] Accept/reject functionality works
- [ ] Can create NCR
- [ ] NCR workflow works (new → in progress → resolved)

#### 7. Financial Workflow (15 min)
- [ ] Can create vendor invoice
- [ ] Invoice verification works
- [ ] Multi-level approval works
- [ ] Payment creation works
- [ ] Ledger entries auto-create
- [ ] Payment methods display correctly

#### 8. Security & Permissions (10 min)
- [ ] User role can view but not delete
- [ ] Manager role has full access
- [ ] Record rules work correctly
- [ ] Portal users cannot access backend data

#### 9. Reporting & Views (10 min)
- [ ] All tree views display correctly
- [ ] Kanban views work
- [ ] Search filters function
- [ ] Grouping options work
- [ ] Stat buttons show correct counts

**Total Testing Time: ~2 hours**

### Performance Testing

```bash
# Check database size
psql -U odoo -d <database> -c "SELECT pg_size_pretty(pg_database_size('<database>'));"

# Check module data
psql -U odoo -d <database> -c "SELECT COUNT(*) FROM vendor_vendor;"

# Check logs for errors
tail -f /var/log/odoo/odoo-server.log | grep ERROR
```

---

## Production Deployment

### Pre-Deployment Checklist

#### 1. Backup Current System
```bash
# Backup database
pg_dump -U odoo -d production_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup filestore
tar -czf filestore_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  ~/.local/share/Odoo/filestore/production_db/

# Backup Odoo configuration
cp /etc/odoo/odoo.conf /etc/odoo/odoo.conf.backup_$(date +%Y%m%d)
```

#### 2. Verify System Requirements
- [ ] Odoo 19 installed and running
- [ ] PostgreSQL 13+ running
- [ ] All dependencies available
- [ ] Sufficient disk space (>10GB free)
- [ ] Sufficient RAM (>4GB available)

#### 3. Test Database Preparation
- [ ] Test database backup created
- [ ] Module tested on test database
- [ ] All workflows validated
- [ ] Performance tested
- [ ] Security tested

#### 4. Production Server Preparation
- [ ] Production database backed up
- [ ] Maintenance mode notification sent to users
- [ ] Change window scheduled
- [ ] Rollback plan prepared

### Production Installation Steps

#### Step 1: Enter Maintenance Mode

```bash
# Stop Odoo service
sudo systemctl stop odoo

# Or create maintenance page (if using nginx)
sudo mv /etc/nginx/sites-available/odoo.conf /etc/nginx/sites-available/odoo.conf.bak
sudo systemctl reload nginx
```

#### Step 2: Deploy Module Files

```bash
# Copy module to production addons directory
sudo cp -r /path/to/vendor_management /opt/odoo/custom-addons/

# Set correct permissions
sudo chown -R odoo:odoo /opt/odoo/custom-addons/vendor_management
sudo chmod -R 755 /opt/odoo/custom-addons/vendor_management

# Verify files
ls -la /opt/odoo/custom-addons/vendor_management
```

#### Step 3: Update Odoo Configuration

Edit `/etc/odoo/odoo.conf`:

```ini
[options]
# Add custom addons path
addons_path = /opt/odoo/odoo/addons,/opt/odoo/custom-addons

# Production settings (NO dev mode!)
# dev_mode = (remove or comment out)

# Log level
log_level = info
log_handler = :INFO

# Workers (adjust based on CPU cores)
workers = 4
max_cron_threads = 2

# Limits
limit_time_cpu = 600
limit_time_real = 1200
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
```

#### Step 4: Install Module in Production

**Option A: Command Line (Recommended)**

```bash
# Install module WITHOUT demo data
sudo -u odoo /opt/odoo/odoo/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d production_db \
  -i vendor_management \
  --without-demo=all \
  --stop-after-init

# Check logs for errors
tail -n 100 /var/log/odoo/odoo-server.log
```

**Option B: Web Interface**

```bash
# Start Odoo first
sudo systemctl start odoo

# Then follow web installation steps
# Remember: DO NOT install demo data in production!
```

#### Step 5: Verify Installation

```bash
# Check module status in database
psql -U odoo -d production_db -c \
  "SELECT name, state FROM ir_module_module WHERE name='vendor_management';"

# Expected output: vendor_management | installed

# Check for errors in log
grep -i error /var/log/odoo/odoo-server.log | tail -20
```

#### Step 6: Start Production Services

```bash
# Start Odoo
sudo systemctl start odoo

# Check status
sudo systemctl status odoo

# Monitor logs
tail -f /var/log/odoo/odoo-server.log
```

#### Step 7: Smoke Test

1. Login to production: `https://your-domain.com`
2. Check "Vendor Management" menu exists
3. Try creating a test vendor (then delete it)
4. Verify all menus are accessible
5. Check user permissions

#### Step 8: Exit Maintenance Mode

```bash
# Restore nginx configuration (if used)
sudo mv /etc/nginx/sites-available/odoo.conf.bak /etc/nginx/sites-available/odoo.conf
sudo systemctl reload nginx

# Send notification to users
# "System is back online. Vendor Management module is now available."
```

---

## Post-Deployment Configuration

### 1. User Access Setup

```
Settings → Users & Companies → Users
```

**Create/Assign Groups:**

| User Role | Group Assignment |
|-----------|------------------|
| Purchase Manager | Vendor Management / Manager |
| Purchase Officer | Vendor Management / User |
| QA Manager | Vendor Management / Manager |
| QA Officer | Vendor Management / User |
| Accounts Manager | Vendor Management / Manager |
| Accounts Officer | Vendor Management / User |

### 2. Initial Data Setup

**Create Vendor Categories:**
```
Vendor Management → Configuration → Vendor Categories
```
- Electronics
- Raw Materials
- Manufacturing
- IT Services
- Logistics
- Construction
- Professional Services
- Office Supplies

**Create Vendor Tags:**
```
Vendor Management → Configuration → Vendor Tags
```
- Preferred Vendor
- Certified
- International
- Local

**Configure Checklist Templates:**
```
Vendor Management → Configuration → Checklist Templates
```
Templates are pre-loaded, but review and customize:
- GST Registration Certificate
- PAN Card
- ISO Certification
- Bank Account Details
- etc.

### 3. Sequence Configuration

Sequences are auto-configured but can be customized:

```
Settings → Technical → Sequences & Identifiers → Sequences
```

Search for:
- Vendor Code (VEN)
- RFQ Number (RFQ)
- Purchase Order (PO)
- GRN Number (GRN)
- NCR Number (NCR)
- Invoice Number (INV)
- Payment Number (PAY)

### 4. Email Configuration

**Configure Outgoing Mail Server:**
```
Settings → Technical → Email → Outgoing Mail Servers
```

**Set up Email Templates:**
```
Settings → Technical → Email → Email Templates
```

Templates to create:
- RFQ Invitation Email
- Quotation Request Reminder
- PO Confirmation Email
- NCR Notification Email
- Document Expiry Alert Email

### 5. Cron Jobs Setup

**Document Expiry Checker:**
```
Settings → Technical → Automation → Scheduled Actions
```

Create new scheduled action:
- Name: Check Vendor Document Expiry
- Model: vendor.document
- Execute: `model.check_document_expiry()`
- Interval: Daily at 9:00 AM

### 6. Company Configuration

**Set Company Details:**
```
Settings → Users & Companies → Companies
```
- Company Name
- Address
- Tax ID
- Currency

---

## Troubleshooting

### Common Issues

#### Issue 1: Module Not Appearing in Apps List

**Symptoms:** Can't find "Vendor Management" in Apps

**Solutions:**
```bash
# 1. Check addons path
grep addons_path /etc/odoo/odoo.conf

# 2. Verify module location
ls -la /opt/odoo/custom-addons/vendor_management/__manifest__.py

# 3. Update apps list
# Settings → Apps → Update Apps List

# 4. Check Odoo logs
tail -f /var/log/odoo/odoo-server.log | grep vendor_management

# 5. Restart Odoo
sudo systemctl restart odoo
```

#### Issue 2: Installation Fails

**Symptoms:** Installation error or stuck

**Solutions:**
```bash
# 1. Check dependencies
psql -U odoo -d production_db -c \
  "SELECT name, state FROM ir_module_module
   WHERE name IN ('base','mail','contacts','product','uom','account','hr','portal');"

# 2. Install missing dependencies first
/opt/odoo/odoo/odoo-bin -c /etc/odoo/odoo.conf -d production_db \
  -i mail,contacts,product,uom,account,hr,portal --stop-after-init

# 3. Check for syntax errors
python3 -m py_compile /opt/odoo/custom-addons/vendor_management/models/*.py

# 4. Check XML syntax
xmllint --noout /opt/odoo/custom-addons/vendor_management/views/*.xml

# 5. Check logs for specific error
grep -A 10 "ERROR.*vendor_management" /var/log/odoo/odoo-server.log
```

#### Issue 3: Menu Not Visible

**Symptoms:** Module installed but no menu

**Solutions:**
```bash
# 1. Clear browser cache
# Ctrl+Shift+R or Cmd+Shift+R

# 2. Check user access groups
# Settings → Users → Select user → Check "Vendor Management / User" group

# 3. Update module
/opt/odoo/odoo/odoo-bin -c /etc/odoo/odoo.conf -d production_db \
  -u vendor_management --stop-after-init

# 4. Check menu records
psql -U odoo -d production_db -c \
  "SELECT name, active FROM ir_ui_menu WHERE name LIKE '%Vendor%';"
```

#### Issue 4: Permission Denied Errors

**Symptoms:** Users can't access features

**Solutions:**
```sql
-- Check access rights
SELECT m.model, g.name, a.perm_read, a.perm_write, a.perm_create, a.perm_unlink
FROM ir_model_access a
JOIN ir_model m ON a.model_id = m.id
JOIN res_groups g ON a.group_id = g.id
WHERE m.model LIKE 'vendor.%';

-- Grant access to missing groups
-- Settings → Users & Companies → Users
-- Assign "Vendor Management / User" or "Vendor Management / Manager"
```

#### Issue 5: Demo Data Not Loading

**Symptoms:** No demo vendors after installation

**Solutions:**
```bash
# 1. Reinstall with demo data flag
/opt/odoo/odoo/odoo-bin -c /etc/odoo/odoo.conf -d test_db \
  -i vendor_management --without-demo=False --stop-after-init

# 2. Manually load demo data (if needed)
psql -U odoo -d test_db -c \
  "SELECT COUNT(*) FROM vendor_vendor WHERE code LIKE 'VEN%';"

# Should return 5 vendors
```

#### Issue 6: Document Upload Fails

**Symptoms:** Can't attach documents

**Solutions:**
```bash
# 1. Check filestore permissions
ls -la ~/.local/share/Odoo/filestore/production_db/

# 2. Set correct permissions
sudo chown -R odoo:odoo ~/.local/share/Odoo/filestore/
sudo chmod -R 755 ~/.local/share/Odoo/filestore/

# 3. Check disk space
df -h

# 4. Check max upload size (Odoo config)
grep limit_request /etc/odoo/odoo.conf
# Increase if needed: limit_request = 8192
```

#### Issue 7: Slow Performance

**Symptoms:** Module is slow to load

**Solutions:**
```bash
# 1. Check workers configuration
grep workers /etc/odoo/odoo.conf
# Recommended: workers = (CPU cores * 2) + 1

# 2. Enable database indexes
psql -U odoo -d production_db
# CREATE INDEX IF NOT EXISTS vendor_vendor_code_idx ON vendor_vendor(code);
# CREATE INDEX IF NOT EXISTS vendor_rfq_state_idx ON vendor_rfq(state);

# 3. Vacuum database
vacuumdb -U odoo -d production_db -f -z -v

# 4. Check server resources
htop
free -h
df -h
```

### Getting Help

**Check Logs:**
```bash
# Odoo server log
tail -f /var/log/odoo/odoo-server.log

# PostgreSQL log
tail -f /var/log/postgresql/postgresql-*.log

# System log
journalctl -u odoo -f
```

**Debug Mode:**
```bash
# Start Odoo in debug mode
/opt/odoo/odoo/odoo-bin -c /etc/odoo/odoo.conf --log-level=debug

# Or enable in browser
URL: https://your-domain.com/web?debug=1
```

**Run Validation Script:**
```bash
cd /opt/odoo/custom-addons/vendor_management
python3 validate_module.py
```

---

## Backup & Rollback

### Create Backup Before Deployment

```bash
#!/bin/bash
# backup_before_deployment.sh

BACKUP_DIR="/opt/odoo/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="production_db"

mkdir -p $BACKUP_DIR

# Backup database
echo "Backing up database..."
pg_dump -U odoo -d $DB_NAME > $BACKUP_DIR/db_${DB_NAME}_${DATE}.sql
gzip $BACKUP_DIR/db_${DB_NAME}_${DATE}.sql

# Backup filestore
echo "Backing up filestore..."
tar -czf $BACKUP_DIR/filestore_${DB_NAME}_${DATE}.tar.gz \
  ~/.local/share/Odoo/filestore/$DB_NAME/

# Backup config
echo "Backing up config..."
cp /etc/odoo/odoo.conf $BACKUP_DIR/odoo.conf.${DATE}

# Backup custom addons
echo "Backing up custom addons..."
tar -czf $BACKUP_DIR/custom_addons_${DATE}.tar.gz \
  /opt/odoo/custom-addons/

echo "Backup completed: $BACKUP_DIR"
ls -lh $BACKUP_DIR/*${DATE}*
```

### Rollback Procedure

If deployment fails, rollback:

```bash
#!/bin/bash
# rollback.sh

BACKUP_DIR="/opt/odoo/backups"
BACKUP_DATE="20251106_120000"  # Replace with actual backup date
DB_NAME="production_db"

# Stop Odoo
sudo systemctl stop odoo

# Restore database
echo "Restoring database..."
dropdb -U odoo $DB_NAME
createdb -U odoo $DB_NAME
gunzip -c $BACKUP_DIR/db_${DB_NAME}_${BACKUP_DATE}.sql.gz | psql -U odoo -d $DB_NAME

# Restore filestore
echo "Restoring filestore..."
rm -rf ~/.local/share/Odoo/filestore/$DB_NAME
tar -xzf $BACKUP_DIR/filestore_${DB_NAME}_${BACKUP_DATE}.tar.gz \
  -C ~/.local/share/Odoo/filestore/

# Restore config
echo "Restoring config..."
cp $BACKUP_DIR/odoo.conf.${BACKUP_DATE} /etc/odoo/odoo.conf

# Remove module files
echo "Removing module..."
rm -rf /opt/odoo/custom-addons/vendor_management

# Restore custom addons (if needed)
# tar -xzf $BACKUP_DIR/custom_addons_${BACKUP_DATE}.tar.gz -C /opt/odoo/

# Start Odoo
sudo systemctl start odoo

echo "Rollback completed"
```

---

## Quick Reference

### Installation Commands

```bash
# Test (with demo data)
/opt/odoo/odoo/odoo-bin -c odoo.conf -d test_db -i vendor_management --without-demo=False

# Production (no demo data)
/opt/odoo/odoo/odoo-bin -c odoo.conf -d prod_db -i vendor_management --without-demo=all --stop-after-init

# Update module
/opt/odoo/odoo/odoo-bin -c odoo.conf -d db_name -u vendor_management --stop-after-init

# Uninstall module
/opt/odoo/odoo/odoo-bin -c odoo.conf -d db_name --uninstall vendor_management --stop-after-init
```

### Service Commands

```bash
# Start Odoo
sudo systemctl start odoo

# Stop Odoo
sudo systemctl stop odoo

# Restart Odoo
sudo systemctl restart odoo

# Status
sudo systemctl status odoo

# Enable auto-start
sudo systemctl enable odoo

# View logs
journalctl -u odoo -f
```

### Database Commands

```bash
# List databases
psql -U odoo -l

# Connect to database
psql -U odoo -d production_db

# Check module status
psql -U odoo -d production_db -c "SELECT name, state FROM ir_module_module WHERE name='vendor_management';"

# Vacuum database
vacuumdb -U odoo -d production_db -f -z
```

---

## Support & Documentation

### Documentation Files

| File | Description |
|------|-------------|
| `README.md` | Module overview |
| `VALIDATION_SUMMARY.md` | Validation report |
| `IMPLEMENTATION_REPORT.md` | Technical details |
| `DEMO_DATA_GUIDE.md` | Demo data and training |
| `DEPLOYMENT_GUIDE.md` | This file |

### Validation Tool

```bash
cd /opt/odoo/custom-addons/vendor_management
python3 validate_module.py
```

### Module Info

```
Name: Vendor Management
Version: 1.0
Depends: base, mail, contacts, product, uom, account, hr, portal
License: LGPL-3
Installable: Yes
Auto Install: No
```

---

## Deployment Timeline

**Recommended Schedule:**

| Phase | Duration | Description |
|-------|----------|-------------|
| **Week 1** | 5 days | Test environment setup and validation |
| **Week 2** | 5 days | User training and UAT |
| **Week 3** | 1 day | Production deployment preparation |
| **Week 4** | 1 day | Production deployment (off-hours) |
| **Week 5+** | Ongoing | Post-deployment support |

**Best Practice:** Deploy on Friday evening or Saturday to have weekend for issue resolution.

---

## Success Criteria

Deployment is successful when:

- ✅ Module installs without errors
- ✅ All menus accessible
- ✅ Users can create vendors
- ✅ Complete workflow works (RFQ → PO → GRN → Invoice → Payment)
- ✅ Security permissions working
- ✅ No errors in log files
- ✅ Performance acceptable (<2 sec page load)
- ✅ Users trained and comfortable with system

---

## Contact & Support

**For Issues:**
1. Check this deployment guide
2. Review `TROUBLESHOOTING` section above
3. Check Odoo logs
4. Run validation script
5. Contact development team

**Emergency Rollback:**
If critical issues occur, execute rollback procedure immediately and notify stakeholders.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-06
**Next Review:** After first production deployment

---

🎉 **You're ready to deploy! Good luck!** 🚀
