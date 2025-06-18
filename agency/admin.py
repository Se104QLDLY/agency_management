from django.contrib import admin
from .models import AgencyType, District, Agency, StaffAgency

class AgencyInline(admin.TabularInline):
    model = Agency
    extra = 0
    fields = ('agency_name', 'agency_type', 'phone_number', 'address', 'email', 'representative', 'reception_date', 'debt_amount', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    show_change_link = True

class StaffAgencyInline(admin.TabularInline):
    model = StaffAgency
    extra = 0
    fields = ('staff_id',)
    show_change_link = True

@admin.register(AgencyType)
class AgencyTypeAdmin(admin.ModelAdmin):
    '''Admin interface for AgencyType model.'''
    list_display = ('agency_type_id', 'type_name', 'max_debt', 'description')
    search_fields = ('type_name',)

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    '''Admin interface for District model.'''
    list_display = ('district_id', 'district_name', 'city_name', 'max_agencies')
    search_fields = ('district_name', 'city_name')
    inlines = [AgencyInline]

@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    '''Admin interface for Agency model.'''
    list_display = ('agency_id', 'agency_name', 'agency_type', 'district', 'phone_number', 'email', 'representative', 'reception_date', 'debt_amount', 'created_at', 'updated_at')
    search_fields = ('agency_name', 'email', 'representative', 'phone_number')
    list_filter = ('agency_type', 'district', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [StaffAgencyInline]

@admin.register(StaffAgency)
class StaffAgencyAdmin(admin.ModelAdmin):
    '''Admin interface for StaffAgency model.'''
    list_display = ('staff_id', 'agency')
    search_fields = ('staff_id', 'agency__agency_name')
    list_filter = ('agency',)
