from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps

class Command(BaseCommand):
    help = 'Resets all PostgreSQL primary key sequences to the max value of their respective columns.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting to sync PostgreSQL sequences..."))
        
        all_models = apps.get_models()
        
        with connection.cursor() as cursor:
            for model in all_models:
                if not model._meta.managed or not model._meta.pk or model._meta.pk.get_internal_type() != 'AutoField':
                    continue

                table_name = model._meta.db_table
                pk_name = model._meta.pk.column

                # Using pg_get_serial_sequence is the most robust way to get sequence name
                sequence_sql = f"SELECT pg_get_serial_sequence('{table_name}', '{pk_name}')"
                
                try:
                    cursor.execute(sequence_sql)
                    result = cursor.fetchone()
                    if not result or not result[0]:
                        self.stdout.write(self.style.WARNING(f"  - No sequence found for {table_name}.{pk_name}. Skipping."))
                        continue
                    
                    sequence_name = result[0]

                    max_id_sql = f"SELECT MAX({pk_name}) FROM {table_name};"
                    cursor.execute(max_id_sql)
                    max_id = cursor.fetchone()[0]

                    if max_id is not None:
                        self.stdout.write(f"  - Resetting sequence '{sequence_name}' for table '{table_name}' to {max_id}.")
                        # setval(sequence, value, is_called=true) ensures the next value will be value + 1
                        cursor.execute(f"SELECT setval('{sequence_name}', {max_id}, true);")
                    else:
                        # If table is empty, reset sequence so the next value is 1
                        self.stdout.write(f"  - Table '{table_name}' is empty. Resetting sequence '{sequence_name}' to 1.")
                        cursor.execute(f"SELECT setval('{sequence_name}', 1, false);")

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error processing {table_name}: {e}"))

        self.stdout.write(self.style.SUCCESS("Sequence sync completed!")) 