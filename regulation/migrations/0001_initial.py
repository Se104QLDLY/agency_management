# Generated by Django 5.2.3 on 2025-06-17 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Regulation",
            fields=[
                (
                    "regulation_key",
                    models.CharField(max_length=50, primary_key=True, serialize=False),
                ),
                ("regulation_value", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                ("last_updated_by", models.IntegerField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Regulation",
                "verbose_name_plural": "Regulations",
                "db_table": "regulation",
                "ordering": ["regulation_key"],
            },
        ),
    ]
