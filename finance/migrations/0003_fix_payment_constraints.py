"""
Migration script to update Payment model status choices
and add necessary constraints for the fixed business logic.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_alter_debtsummary_table_alter_payment_table_and_more'),  # Correct: Latest migration
    ]

    operations = [
        # Update Payment status field with proper choices
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Đang chờ xử lý'),
                    ('confirmed', 'Đã xác nhận'),
                    ('cancelled', 'Đã hủy')
                ],
                default='pending',
                max_length=20,
                help_text='Trạng thái thanh toán',
                db_column='status'
            ),
        ),
        
        # Add check constraint for positive payment amounts
        migrations.RunSQL(
            "ALTER TABLE finance.payment ADD CONSTRAINT payment_amount_positive CHECK (amount_collected > 0);",
            reverse_sql="ALTER TABLE finance.payment DROP CONSTRAINT IF EXISTS payment_amount_positive;"
        ),
        
        # Add check constraint for debt amounts (cannot be negative)
        migrations.RunSQL(
            "ALTER TABLE agency.agency ADD CONSTRAINT agency_debt_non_negative CHECK (debt_amount >= 0);",
            reverse_sql="ALTER TABLE agency.agency DROP CONSTRAINT IF EXISTS agency_debt_non_negative;"
        ),
        
        # Add performance indexes
        migrations.RunSQL(
            """
            CREATE INDEX IF NOT EXISTS idx_issue_status ON inventory.issue(status);
            CREATE INDEX IF NOT EXISTS idx_payment_status ON finance.payment(status);
            CREATE INDEX IF NOT EXISTS idx_issue_agency_status ON inventory.issue(agency_id, status);
            CREATE INDEX IF NOT EXISTS idx_payment_agency_status ON finance.payment(agency_id, status);
            """,
            reverse_sql="""
            DROP INDEX IF EXISTS inventory.idx_issue_status;
            DROP INDEX IF EXISTS finance.idx_payment_status;
            DROP INDEX IF EXISTS inventory.idx_issue_agency_status;
            DROP INDEX IF EXISTS finance.idx_payment_agency_status;
            """
        ),
    ]
