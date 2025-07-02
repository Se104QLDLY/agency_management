from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0003_create_auth_schema'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
            ALTER TABLE "auth"."account"
            ADD CONSTRAINT account_role_chk
            CHECK (account_role IN (\'admin\',\'staff\',\'agent\'));
            ''',
            reverse_sql='''
            ALTER TABLE "auth"."account" DROP CONSTRAINT IF EXISTS account_role_chk;
            '''
        ),
    ] 