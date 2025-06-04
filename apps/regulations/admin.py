from django.contrib import admin
from .models import Regulation

@admin.register(Regulation)
class RegulationAdmin(admin.ModelAdmin):
    list_display = ('regulation_key', 'regulation_value', 'description', 'last_updated_by', 'updated_at')
    search_fields = ('regulation_key', 'regulation_value', 'description')
    list_filter = ('last_updated_by', 'updated_at')
    date_hierarchy = 'updated_at'
