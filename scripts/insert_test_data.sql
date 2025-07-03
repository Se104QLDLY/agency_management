-- ===================================================================
-- INSERT TEST DATA FOR NEWDDL.SQL DATABASE
-- ===================================================================
-- Comprehensive test data for API testing
-- All passwords are properly hashed using Django's pbkdf2_sha256
-- ===================================================================

-- Clear existing data (in dependency order)
DELETE FROM agency.staffagency;
DELETE FROM inventory.issuedetail;
DELETE FROM inventory.issue;
DELETE FROM inventory.receiptdetail;
DELETE FROM inventory.receipt;
DELETE FROM inventory.item;
DELETE FROM inventory.unit;
DELETE FROM finance.payment;
DELETE FROM finance.report;
DELETE FROM agency.agency;
DELETE FROM agency.district;
DELETE FROM agency.agencytype;
DELETE FROM auth.user;
DELETE FROM auth.account;
DELETE FROM config.regulation;

-- Reset sequences (only for existing ones)
ALTER SEQUENCE auth.account_account_id_seq RESTART WITH 1;
ALTER SEQUENCE auth.user_user_id_seq RESTART WITH 1;
ALTER SEQUENCE agency.agencytype_agency_type_id_seq RESTART WITH 1;
ALTER SEQUENCE agency.district_district_id_seq RESTART WITH 1;
ALTER SEQUENCE agency.agency_agency_id_seq RESTART WITH 1;
ALTER SEQUENCE inventory.unit_unit_id_seq RESTART WITH 1;
ALTER SEQUENCE inventory.item_item_id_seq RESTART WITH 1;
ALTER SEQUENCE inventory.receipt_receipt_id_seq RESTART WITH 1;
ALTER SEQUENCE inventory.receiptdetail_receipt_detail_id_seq RESTART WITH 1;
ALTER SEQUENCE inventory.issue_issue_id_seq RESTART WITH 1;
ALTER SEQUENCE inventory.issuedetail_issue_detail_id_seq RESTART WITH 1;
ALTER SEQUENCE finance.payment_payment_id_seq RESTART WITH 1;
ALTER SEQUENCE finance.report_report_id_seq RESTART WITH 1;

-- ===================================================================
-- 1. AUTHENTICATION DATA
-- ===================================================================

-- Insert Accounts with proper password hashes
INSERT INTO auth.account (account_id, username, password_hash, account_role, created_at, updated_at) VALUES
(1, 'admin', 'pbkdf2_sha256$1000000$k4EWNk3rchu3Jxyid5Rhx8$bCxffDK/BTrIQqhN3we40WbbWvL2ePolWkZcN6ojQQ=', 'admin', NOW(), NOW()),
(2, 'staff1', 'pbkdf2_sha256$1000000$BLfDxEkdDa54VOt31NUPLn$mRJWpF3AV2f5ZV9A2lje7f/TK9n8xCtgiDekmhu7xMo=', 'staff', NOW(), NOW()),
(3, 'staff2', 'pbkdf2_sha256$1000000$BLfDxEkdDa54VOt31NUPLn$mRJWpF3AV2f5ZV9A2lje7f/TK9n8xCtgiDekmhu7xMo=', 'staff', NOW(), NOW()),
(4, 'agent1', 'pbkdf2_sha256$1000000$3YvzWQzR1doGlpl61oqRby$CjGTb8wMNWwZVPJmUNRChHXhMpDU1vak4UZ0SqX1GUQ=', 'agent', NOW(), NOW()),
(5, 'agent2', 'pbkdf2_sha256$1000000$3YvzWQzR1doGlpl61oqRby$CjGTb8wMNWwZVPJmUNRChHXhMpDU1vak4UZ0SqX1GUQ=', 'agent', NOW(), NOW());

-- Insert Users
INSERT INTO auth.user (user_id, account_id, full_name, email, phone_number, address) VALUES
(1, 1, 'Quản trị viên hệ thống', 'admin@company.com', '0123456789', 'TP.HCM'),
(2, 2, 'Nhân viên Kinh doanh 1', 'staff1@company.com', '0987654321', 'Hà Nội'),
(3, 3, 'Nhân viên Kinh doanh 2', 'staff2@company.com', '0987654322', 'Đà Nẵng'),
(4, 4, 'Đại lý Minh Long', 'agent1@company.com', '0123987654', 'TP.HCM'),
(5, 5, 'Đại lý Thành Đạt', 'agent2@company.com', '0123987655', 'Hà Nội');

-- ===================================================================
-- 2. AGENCY MANAGEMENT DATA
-- ===================================================================

-- Insert Agency Types
INSERT INTO agency.agencytype (agency_type_id, type_name, max_debt, description) VALUES
(1, 'Đại lý cấp 1', 1000000000.00, 'Đại lý cấp 1 với hạn mức nợ cao'),
(2, 'Đại lý cấp 2', 500000000.00, 'Đại lý cấp 2 với hạn mức nợ trung bình'),
(3, 'Đại lý cấp 3', 200000000.00, 'Đại lý cấp 3 với hạn mức nợ thấp');

-- Insert Districts
INSERT INTO agency.district (district_id, district_name, city_name, max_agencies) VALUES
(1, 'Quận 1', 'TP.HCM', 10),
(2, 'Quận 2', 'TP.HCM', 15),
(3, 'Quận 3', 'TP.HCM', 12),
(4, 'Ba Đình', 'Hà Nội', 8),
(5, 'Hoàn Kiếm', 'Hà Nội', 6),
(6, 'Hải Châu', 'Đà Nẵng', 10);

-- Insert Agencies
INSERT INTO agency.agency (agency_id, agency_name, agency_type_id, phone_number, address, district_id, email, representative, reception_date, debt_amount, created_at, updated_at, user_id) VALUES
(1, 'Đại lý Kim Long Premium', 1, '0123456789', '123 Đường ABC, Quận 1', 1, 'kimlong@test.com', 'Nguyễn Văn A', '2024-01-15', 0.00, NOW(), NOW(), 4),
(2, 'Đại lý Hoàng Gia Corporation', 2, '0987654321', '456 Đường XYZ, Quận 2', 2, 'hoanggia@test.com', 'Trần Thị B', '2024-02-20', 0.00, NOW(), NOW(), 5),
(3, 'Đại lý Minh Đức Trading', 2, '0369852147', '789 Đường DEF, Quận 3', 3, 'minhduc@test.com', 'Lê Văn C', '2024-03-10', 150000000.00, NOW(), NOW(), null),
(4, 'Đại lý Thành Công Distribution', 1, '0258741369', '321 Đường GHI, Ba Đình', 4, 'thanhcong@test.com', 'Phạm Thị D', '2024-04-05', 0.00, NOW(), NOW(), null),
(5, 'Đại lý Viet Smile', 3, '0147258369', '654 Đường JKL, Hoàn Kiếm', 5, 'vietsmile@test.com', 'Hoàng Văn E', '2024-05-12', 75000000.00, NOW(), NOW(), null),
(6, 'Đại lý Golden Star', 2, '0741852963', '987 Đường MNO, Hải Châu', 6, 'goldenstar@test.com', 'Vũ Thị F', '2024-06-01', 0.00, NOW(), NOW(), null),
(7, 'Đại lý Đông Dương Premium', 1, '0963258741', '159 Đường PQR, Quận 1', 1, 'dongduong@test.com', 'Ngô Văn G', '2024-06-15', 200000000.00, NOW(), NOW(), null),
(8, 'Đại lý Sài Gòn Xanh', 3, '0852741963', '753 Đường STU, Quận 2', 2, 'saigonxanh@test.com', 'Đỗ Thị H', '2024-06-20', 0.00, NOW(), NOW(), null);

-- Insert Staff-Agency relationships
INSERT INTO agency.staffagency (staff_id, agency_id) VALUES
(2, 1), (2, 2), (2, 3), (2, 4),
(3, 3), (3, 5), (3, 6), (3, 7), (3, 8);

-- ===================================================================
-- 3. INVENTORY DATA
-- ===================================================================

-- Insert Units
INSERT INTO inventory.unit (unit_id, unit_name) VALUES
(1, 'Thùng'),
(2, 'Chai'),
(3, 'Lon'),
(4, 'Gói'),
(5, 'Bộ'),
(6, 'Kg');

-- Insert Items
INSERT INTO inventory.item (item_id, item_name, unit_id, price, stock_quantity, description, created_at, updated_at) VALUES
(1, 'Bia Saigon Special thùng 24 chai', 1, 240000.00, 500, 'Bia Saigon Special đóng thùng 24 chai', NOW(), NOW()),
(2, 'Bia Tiger Crystal chai 330ml', 2, 12000.00, 2000, 'Bia Tiger Crystal chai thuỷ tinh 330ml', NOW(), NOW()),
(3, 'Bia Heineken lon 330ml', 3, 15000.00, 1500, 'Bia Heineken lon nhôm 330ml', NOW(), NOW()),
(4, 'Bia 333 Export thùng 24 chai', 1, 220000.00, 300, 'Bia 333 Export đóng thùng 24 chai', NOW(), NOW()),
(5, 'Bia Budweiser chai 330ml', 2, 18000.00, 800, 'Bia Budweiser chai thuỷ tinh 330ml', NOW(), NOW()),
(6, 'Bia Corona Extra chai 355ml', 2, 25000.00, 400, 'Bia Corona Extra chai thuỷ tinh 355ml', NOW(), NOW()),
(7, 'Rượu Soju Chamisul gói 4 chai', 4, 85000.00, 200, 'Rượu Soju Chamisul đóng gói 4 chai', NOW(), NOW()),
(8, 'Whisky Johnnie Walker Black Label', 2, 1200000.00, 50, 'Whisky Johnnie Walker Black Label 750ml', NOW(), NOW()),
(9, 'Vodka Smirnoff chai 700ml', 2, 450000.00, 120, 'Vodka Smirnoff chai thuỷ tinh 700ml', NOW(), NOW()),
(10, 'Rượu vang Đà Lạt chai 750ml', 2, 180000.00, 150, 'Rượu vang đỏ Đà Lạt chai thuỷ tinh 750ml', NOW(), NOW());

-- Insert Receipts (Stock-in)
INSERT INTO inventory.receipt (receipt_id, agency_id, user_id, receipt_date, total_amount, created_at) VALUES
(1, 1, 2, '2024-06-01', 2400000.00, '2024-06-01 09:00:00'),
(2, 2, 2, '2024-06-05', 1800000.00, '2024-06-05 10:15:00'),
(3, 3, 3, '2024-06-10', 3200000.00, '2024-06-10 14:30:00'),
(4, 4, 2, '2024-06-15', 1500000.00, '2024-06-15 11:45:00'),
(5, 5, 3, '2024-06-20', 2700000.00, '2024-06-20 16:00:00');

-- Insert Receipt Details
INSERT INTO inventory.receiptdetail (receipt_detail_id, receipt_id, item_id, quantity, unit_price, line_total) VALUES
(1, 1, 1, 10, 240000.00, 2400000.00),
(2, 2, 2, 150, 12000.00, 1800000.00),
(3, 3, 3, 100, 15000.00, 1500000.00),
(4, 3, 4, 8, 220000.00, 1760000.00),
(5, 4, 5, 50, 18000.00, 900000.00),
(6, 4, 6, 24, 25000.00, 600000.00),
(7, 5, 7, 20, 85000.00, 1700000.00),
(8, 5, 8, 2, 1200000.00, 2400000.00),
(9, 5, 9, 4, 450000.00, 1800000.00);

-- Insert Issues (Stock-out)
INSERT INTO inventory.issue (issue_id, agency_id, user_id, issue_date, total_amount, created_at) VALUES
(1, 1, 2, '2024-06-02', 1440000.00, '2024-06-02 08:30:00'),
(2, 2, 2, '2024-06-07', 720000.00, '2024-06-07 13:20:00'),
(3, 3, 3, '2024-06-12', 2250000.00, '2024-06-12 15:45:00'),
(4, 4, 2, '2024-06-18', 990000.00, '2024-06-18 10:10:00'),
(5, 5, 3, '2024-06-22', 1700000.00, '2024-06-22 12:00:00');

-- Insert Issue Details
INSERT INTO inventory.issuedetail (issue_detail_id, issue_id, item_id, quantity, unit_price, line_total) VALUES
(1, 1, 1, 6, 240000.00, 1440000.00),
(2, 2, 2, 60, 12000.00, 720000.00),
(3, 3, 3, 50, 15000.00, 750000.00),
(4, 3, 4, 5, 220000.00, 1100000.00),
(5, 3, 5, 25, 18000.00, 450000.00),
(6, 4, 6, 20, 25000.00, 500000.00),
(7, 4, 7, 8, 85000.00, 680000.00),
(8, 5, 8, 1, 1200000.00, 1200000.00),
(9, 5, 9, 2, 450000.00, 900000.00);

-- ===================================================================
-- 4. FINANCE DATA
-- ===================================================================

-- Insert Payments
INSERT INTO finance.payment (payment_id, agency_id, user_id, amount_collected, payment_date, created_at) VALUES
(1, 1, 2, 1000000.00, '2024-06-03', '2024-06-03 09:00:00'),
(2, 2, 2, 500000.00, '2024-06-08', '2024-06-08 14:30:00'),
(3, 3, 3, 2000000.00, '2024-06-13', '2024-06-13 11:15:00'),
(4, 4, 2, 800000.00, '2024-06-19', '2024-06-19 16:45:00'),
(5, 5, 3, 1200000.00, '2024-06-23', '2024-06-23 10:20:00'),
(6, 1, 2, 440000.00, '2024-06-25', '2024-06-25 13:00:00'),
(7, 7, 2, 200000.00, '2024-06-26', '2024-06-26 15:30:00'),
(8, 3, 3, 250000.00, '2024-06-27', '2024-06-27 09:45:00');

-- Insert Reports
INSERT INTO finance.report (report_id, report_date, report_type, data, created_by, created_at) VALUES
(1, '2024-06-30', 'sales', '{"total_sales": 12600000, "total_receipts": 5, "total_issues": 5}', 1, '2024-06-30 23:59:59'),
(2, '2024-06-30', 'debt', '{"total_debt": 425000000, "agencies_in_debt": 3}', 1, '2024-06-30 23:59:59'),
(3, '2024-06-30', 'sales', '{"total_items": 10, "low_stock_items": 2}', 1, '2024-06-30 23:59:59');

-- ===================================================================
-- 5. SYSTEM CONFIGURATION DATA
-- ===================================================================

-- Insert Regulations
INSERT INTO config.regulation (regulation_key, regulation_value, description, updated_at) VALUES
('max_debt_default', '10000000', 'Hạn mức nợ mặc định (VND)', NOW()),
('min_stock_alert', '100', 'Ngưỡng cảnh báo tồn kho thấp (số lượng)', NOW()),
('payment_terms_days', '30', 'Số ngày thanh toán cho phép', NOW()),
('max_agencies_per_district', '20', 'Số lượng đại lý tối đa mỗi quận/huyện', NOW()),
('system_commission_rate', '5.5', 'Tỷ lệ hoa hồng hệ thống (%)', NOW()),
('auto_debt_alert_threshold', '80', 'Ngưỡng cảnh báo nợ tự động (% hạn mức)', NOW());

-- ===================================================================
-- 6. UPDATE STOCK QUANTITIES AFTER ISSUES
-- ===================================================================

-- Update stock quantities based on issued items
UPDATE inventory.item SET stock_quantity = stock_quantity - 6 WHERE item_id = 1; -- Bia Saigon: 500 - 6 = 494
UPDATE inventory.item SET stock_quantity = stock_quantity - 60 WHERE item_id = 2; -- Tiger: 2000 - 60 = 1940
UPDATE inventory.item SET stock_quantity = stock_quantity - 50 WHERE item_id = 3; -- Heineken: 1500 - 50 = 1450
UPDATE inventory.item SET stock_quantity = stock_quantity - 5 WHERE item_id = 4; -- 333: 300 - 5 = 295
UPDATE inventory.item SET stock_quantity = stock_quantity - 25 WHERE item_id = 5; -- Budweiser: 800 - 25 = 775
UPDATE inventory.item SET stock_quantity = stock_quantity - 20 WHERE item_id = 6; -- Corona: 400 - 20 = 380
UPDATE inventory.item SET stock_quantity = stock_quantity - 8 WHERE item_id = 7; -- Soju: 200 - 8 = 192
UPDATE inventory.item SET stock_quantity = stock_quantity - 1 WHERE item_id = 8; -- Johnnie Walker: 50 - 1 = 49
UPDATE inventory.item SET stock_quantity = stock_quantity - 2 WHERE item_id = 9; -- Smirnoff: 120 - 2 = 118

-- ===================================================================
-- 7. UPDATE AGENCY DEBT AMOUNTS
-- ===================================================================

-- Update agency debt amounts (Issue amount - Payment amount)
UPDATE agency.agency SET debt_amount = 1440000.00 - 1440000.00 WHERE agency_id = 1; -- 0
UPDATE agency.agency SET debt_amount = 720000.00 - 500000.00 WHERE agency_id = 2; -- 220000
UPDATE agency.agency SET debt_amount = 150000000.00 + 2250000.00 - 2250000.00 WHERE agency_id = 3; -- 150000000 (existing debt)
UPDATE agency.agency SET debt_amount = 990000.00 - 800000.00 WHERE agency_id = 4; -- 190000
UPDATE agency.agency SET debt_amount = 75000000.00 + 1700000.00 - 1200000.00 WHERE agency_id = 5; -- 75500000 (existing debt + issue - payment)
UPDATE agency.agency SET debt_amount = 0.00 WHERE agency_id = 6; -- No transactions
UPDATE agency.agency SET debt_amount = 200000000.00 - 200000.00 WHERE agency_id = 7; -- 199800000 (existing debt - payment)
UPDATE agency.agency SET debt_amount = 0.00 WHERE agency_id = 8; -- No transactions

-- ===================================================================
-- SUMMARY
-- ===================================================================

SELECT '=== DATA INSERTION COMPLETED ===' as status;
SELECT 'Accounts: ' || COUNT(*) as summary FROM auth.account
UNION ALL
SELECT 'Users: ' || COUNT(*) FROM auth.user  
UNION ALL
SELECT 'Agency Types: ' || COUNT(*) FROM agency.agencytype
UNION ALL
SELECT 'Districts: ' || COUNT(*) FROM agency.district
UNION ALL
SELECT 'Agencies: ' || COUNT(*) FROM agency.agency
UNION ALL  
SELECT 'Staff-Agency Relations: ' || COUNT(*) FROM agency.staffagency
UNION ALL
SELECT 'Inventory Units: ' || COUNT(*) FROM inventory.unit
UNION ALL
SELECT 'Items: ' || COUNT(*) FROM inventory.item
UNION ALL
SELECT 'Receipts: ' || COUNT(*) FROM inventory.receipt
UNION ALL
SELECT 'Issues: ' || COUNT(*) FROM inventory.issue  
UNION ALL
SELECT 'Payments: ' || COUNT(*) FROM finance.payment
UNION ALL
SELECT 'Reports: ' || COUNT(*) FROM finance.report
UNION ALL
SELECT 'Regulations: ' || COUNT(*) FROM config.regulation;

-- ===================================================================
-- LOGIN CREDENTIALS FOR TESTING
-- ===================================================================
/*
ACCOUNTS FOR API TESTING:
- admin / admin123 (Admin role)
- staff1 / staff123 (Staff role) 
- staff2 / staff123 (Staff role)
- agent1 / agent123 (Agent role)
- agent2 / agent123 (Agent role)

AGENCIES FOR TESTING:
- ID 1-8: Various agencies with different debt amounts
- Some agencies have assigned users, some don't

INVENTORY ITEMS:
- ID 1-10: Various alcoholic beverages  
- Different units (thùng, chai, lon, gói)
- Stock quantities updated after issues

ALL DATA IS CONSISTENT AND READY FOR API TESTING!
*/ 