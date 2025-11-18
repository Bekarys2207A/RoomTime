from django.contrib import admin
from .models import Resource, TimeSlot

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'capacity', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'location']

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['resource', 'starts_at', 'ends_at', 'status']
    list_filter = ['status', 'resource']