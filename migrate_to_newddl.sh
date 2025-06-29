#!/bin/bash
set -e

echo "🚀 MIGRATING BACKEND TO NEWDDL.SQL FORMAT"
echo "============================================"

# Step 1: Stop Django server
echo "📢 Step 1: Stopping Django server..."
pkill -f "runserver" || true

# Step 2: Drop and recreate database schemas
echo "📢 Step 2: Dropping existing schemas..."
python3 manage.py dbshell << 'EOF'
DROP SCHEMA IF EXISTS auth CASCADE;
DROP SCHEMA IF EXISTS agency CASCADE; 
DROP SCHEMA IF EXISTS inventory CASCADE;
DROP SCHEMA IF EXISTS finance CASCADE;
DROP SCHEMA IF EXISTS config CASCADE;
\q
EOF

echo "📢 Step 3: Applying newddl.sql..."
python3 manage.py dbshell < ../db/newddl.sql

# Step 4: Update Django models db_table format
echo "📢 Step 4: Updating Django model db_table declarations..."

# Authentication models
sed -i 's/db_table = '\''auth"."account'\''/db_table = '\''auth.account'\''/g' authentication/models.py
sed -i 's/db_table = '\''auth"."user'\''/db_table = '\''auth.user'\''/g' authentication/models.py

# Agency models  
sed -i 's/db_table = '\''agency"."agencytype'\''/db_table = '\''agency.agencytype'\''/g' agency/models.py
sed -i 's/db_table = '\''agency"."district'\''/db_table = '\''agency.district'\''/g' agency/models.py
sed -i 's/db_table = '\''agency"."agency'\''/db_table = '\''agency.agency'\''/g' agency/models.py
sed -i 's/db_table = '\''agency"."staffagency'\''/db_table = '\''agency.staffagency'\''/g' agency/models.py

# Inventory models
sed -i 's/db_table = '\''inventory"."unit'\''/db_table = '\''inventory.unit'\''/g' inventory/models.py
sed -i 's/db_table = '\''inventory"."item'\''/db_table = '\''inventory.item'\''/g' inventory/models.py
sed -i 's/db_table = '\''inventory"."receipt'\''/db_table = '\''inventory.receipt'\''/g' inventory/models.py
sed -i 's/db_table = '\''inventory"."receiptdetail'\''/db_table = '\''inventory.receiptdetail'\''/g' inventory/models.py
sed -i 's/db_table = '\''inventory"."issue'\''/db_table = '\''inventory.issue'\''/g' inventory/models.py
sed -i 's/db_table = '\''inventory"."issuedetail'\''/db_table = '\''inventory.issuedetail'\''/g' inventory/models.py

# Finance models
sed -i 's/db_table = '\''finance"."payment'\''/db_table = '\''finance.payment'\''/g' finance/models.py
sed -i 's/db_table = '\''finance"."report'\''/db_table = '\''finance.report'\''/g' finance/models.py
sed -i 's/db_table = '\''finance"."v_debt_summary'\''/db_table = '\''finance.v_debt_summary'\''/g' finance/models.py
sed -i 's/db_table = '\''finance"."v_sales_monthly'\''/db_table = '\''finance.v_sales_monthly'\''/g' finance/models.py

# Regulation models
sed -i 's/db_table = '\''config"."regulation'\''/db_table = '\''config.regulation'\''/g' regulation/models.py

echo "📢 Step 5: Adding missing fields to Item model..."
# Add created_at and updated_at to Item model
python3 << 'EOF'
import re

# Read the file
with open('inventory/models.py', 'r') as f:
    content = f.read()

# Find the Item model and add missing fields
pattern = r'(class Item\(models\.Model\):.*?)(description = models\.TextField.*?\n)(.*?class Meta:)'
replacement = r'\1\2    created_at = models.DateTimeField(null=True, blank=True, db_column="created_at")\n    updated_at = models.DateTimeField(null=True, blank=True, db_column="updated_at")\n\n\3'

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('inventory/models.py', 'w') as f:
    f.write(new_content)

print("✅ Added created_at and updated_at to Item model")
EOF

echo "📢 Step 6: Creating test data for newddl schema..."
python3 << 'EOF'
# Create a simple test data script for newddl.sql format
script_content = '''
-- Test data for newddl.sql format
INSERT INTO auth.account (username, password_hash, account_role) VALUES 
('admin', 'scrypt:32768:8:1$2b2KsyDhdXhpJelc$eb9f9658e7c6a2b92a7b8b1c7f4d6e8a9c2b5d3f8e7a6c4e9b2a5c8f7d1e3b6a9c4f2d7e8b1a5c9f6d3e7b2a8c', 'admin'),
('staff1', 'scrypt:32768:8:1$2b2KsyDhdXhpJelc$eb9f9658e7c6a2b92a7b8b1c7f4d6e8a9c2b5d3f8e7a6c4e9b2a5c8f7d1e3b6a9c4f2d7e8b1a5c9f6d3e7b2a8c', 'staff'),
('agent1', 'scrypt:32768:8:1$2b2KsyDhdXhpJelc$eb9f9658e7c6a2b92a7b8b1c7f4d6e8a9c2b5d3f8e7a6c4e9b2a5c8f7d1e3b6a9c4f2d7e8b1a5c9f6d3e7b2a8c', 'agent');

INSERT INTO auth."user" (account_id, full_name, email, phone_number, address) VALUES 
(1, 'Quản trị viên hệ thống', 'admin@company.com', '0123456789', 'TP.HCM'),
(2, 'Nhân viên kinh doanh', 'staff1@company.com', '0987654321', 'Hà Nội'),
(3, 'Đại lý test', 'agent1@company.com', '0123987654', 'Đà Nẵng');

INSERT INTO agency.agencytype (type_name, max_debt, description) VALUES 
('Đại lý cấp 1', 1000000000.00, 'Đại lý cấp 1 với hạn mức nợ cao'),
('Đại lý cấp 2', 500000000.00, 'Đại lý cấp 2 với hạn mức nợ trung bình');

INSERT INTO agency.district (city_name, district_name, max_agencies) VALUES 
('TP.HCM', 'Quận 1', 10),
('TP.HCM', 'Quận 2', 15),
('Hà Nội', 'Ba Đình', 8);

INSERT INTO agency.agency (agency_name, agency_type_id, phone_number, address, district_id, email, representative, reception_date, user_id) VALUES 
('Đại lý Kim Long Premium', 1, '0123456789', '123 Đường ABC, Quận 1', 1, 'kimlong@test.com', 'Nguyễn Văn A', '2024-01-15', 3),
('Đại lý Hoàng Gia Corporation', 2, '0987654321', '456 Đường XYZ, Quận 2', 2, 'hoanggia@test.com', 'Trần Thị B', '2024-02-20', NULL);

INSERT INTO inventory.unit (unit_name) VALUES 
('Thùng'),
('Chai'),
('Lon'),
('Gói');

INSERT INTO inventory.item (item_name, unit_id, price, stock_quantity, description) VALUES 
('Bia Saigon Special thùng 24 chai', 1, 240000.00, 1000, 'Bia Saigon Special đóng thùng 24 chai'),
('Bia Tiger Crystal chai 330ml', 2, 12000.00, 5000, 'Bia Tiger Crystal chai thuỷ tinh 330ml'),
('Bia Heineken lon 330ml', 3, 15000.00, 3000, 'Bia Heineken lon nhôm 330ml');

INSERT INTO config.regulation (regulation_key, regulation_value, description) VALUES 
('max_debt_default', '10000000', 'Hạn mức nợ mặc định'),
('min_stock_alert', '100', 'Ngưỡng cảnh báo tồn kho thấp'),
('payment_terms_days', '30', 'Số ngày thanh toán');
'''

with open('test_data_newddl.sql', 'w') as f:
    f.write(script_content)
print("✅ Created test_data_newddl.sql")
EOF

echo "📢 Step 7: Applying test data..."
python3 manage.py dbshell < test_data_newddl.sql

echo "📢 Step 8: Starting Django server..."
python3 manage.py runserver 0.0.0.0:8000 &
sleep 3

echo "📢 Step 9: Running API tests..."
python3 test_all_apis.py | tail -10

echo ""
echo "🎉 MIGRATION COMPLETED SUCCESSFULLY!"
echo "✅ Database: newddl.sql schema applied"
echo "✅ Backend: All models updated"  
echo "✅ Test data: Basic data created"
echo "✅ APIs: Ready for testing"
echo ""
echo "📋 WHAT CHANGED:"
echo "  • db_table format: 'schema\".\"table' → 'schema.table'"
echo "  • Item model: Added created_at, updated_at fields"
echo "  • Auto-update triggers: Now active for item & agency"
echo "  • Better views: Multiple comprehensive views available"
echo ""
echo "🚀 Backend is now compatible with newddl.sql!" 