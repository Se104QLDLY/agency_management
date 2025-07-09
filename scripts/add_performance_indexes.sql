# Database Index Optimization for Agency Management System
# Run these SQL commands to improve performance on status-based queries

-- Add indexes for status fields
CREATE INDEX IF NOT EXISTS idx_issue_status ON inventory.issue(status);
CREATE INDEX IF NOT EXISTS idx_receipt_status ON inventory.receipt(status);
CREATE INDEX IF NOT EXISTS idx_payment_status ON finance.payment(status);

-- Add composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_issue_agency_status ON inventory.issue(agency_id, status);
CREATE INDEX IF NOT EXISTS idx_issue_date_status ON inventory.issue(issue_date, status);
CREATE INDEX IF NOT EXISTS idx_payment_agency_status ON finance.payment(agency_id, status);

-- Add indexes for debt calculations
CREATE INDEX IF NOT EXISTS idx_agency_debt_amount ON agency.agency(debt_amount);
CREATE INDEX IF NOT EXISTS idx_agency_type_max_debt ON agency.agencytype(max_debt);

-- Add indexes for stock queries
CREATE INDEX IF NOT EXISTS idx_item_stock_quantity ON inventory.item(stock_quantity);

-- Add partial indexes for active records only (PostgreSQL specific)
CREATE INDEX IF NOT EXISTS idx_issue_processing ON inventory.issue(issue_id) WHERE status = 'processing';
CREATE INDEX IF NOT EXISTS idx_issue_confirmed ON inventory.issue(issue_id) WHERE status = 'confirmed';
CREATE INDEX IF NOT EXISTS idx_payment_confirmed ON finance.payment(payment_id) WHERE status = 'confirmed';

-- Statistics update for better query planning
ANALYZE inventory.issue;
ANALYZE inventory.receipt;
ANALYZE finance.payment;
ANALYZE agency.agency;
ANALYZE inventory.item;
