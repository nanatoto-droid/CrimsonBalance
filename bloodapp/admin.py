from django.contrib import admin
from .models import *
from django.utils.html import format_html

@admin.register(BloodDonation)
class BloodDonationAdmin(admin.ModelAdmin):
    list_display = ['donor', 'donation_date', 'blood_group', 'quantity_ml', 'is_processed']
    list_filter = ['blood_group', 'is_processed', 'donation_date']
    search_fields = ['donor__username', 'donor__email']

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'blood_group', 'units_required', 'urgency', 'is_fulfilled']
    list_filter = ['blood_group', 'urgency', 'is_fulfilled']
    search_fields = ['patient_name', 'recipient__username']

@admin.register(InformationPost)
class InformationPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'created_at', 'is_published']
    list_filter = ['category', 'is_published', 'created_at']
    search_fields = ['title', 'content']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'appointment_type', 'scheduled_date', 'status']
    list_filter = ['status', 'appointment_type', 'scheduled_date']

@admin.register(BloodInventory)
class BloodInventoryAdmin(admin.ModelAdmin):
    list_display = ['blood_group', 'available_units', 'critical_level', 'last_updated']
    list_editable = ['available_units', 'critical_level']


class BloodInventoryAdmin(admin.ModelAdmin):
    list_display = ['blood_group', 'available_units', 'critical_level', 'status_indicator', 'last_updated']
    
    def status_indicator(self, obj):
        if obj.is_critical():
            return format_html('<span style="color: red; font-weight: bold;">● CRITICAL</span>')
        elif obj.available_units < 20:
            return format_html('<span style="color: orange; font-weight: bold;">● LOW</span>')
        else:
            return format_html('<span style="color: green; font-weight: bold;">● GOOD</span>')
    status_indicator.short_description = 'Status'   