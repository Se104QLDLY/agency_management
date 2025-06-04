from django.contrib import admin
from .models import District, AgencyType, Agency

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'max_agencies')
    search_fields = ('name', 'city')
    list_filter = ('city',)

@admin.register(AgencyType)
class AgencyTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name', 'max_debt', 'description')
    search_fields = ('type_name', 'description')

@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'agency_type', 'district', 'address', 'phone', 'email', 'representative', 'reception_date', 'debt', 'created_at', 'updated_at')
    search_fields = ('name', 'phone', 'email', 'representative')
    list_filter = ('agency_type', 'district', 'created_at')
    date_hierarchy = 'created_at'
