from django.contrib import admin
from .models import Regulation

@admin.register(Regulation)
class RegulationAdmin(admin.ModelAdmin):
    '''Admin interface for Regulation model.'''
    list_display = ('regulation_key', 'regulation_value', 'description', 'last_updated_by', 'updated_at')
    search_fields = ('regulation_key', 'regulation_value', 'description')
    list_filter = ('updated_at',)
    readonly_fields = ('updated_at',)
