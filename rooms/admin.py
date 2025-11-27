from django.contrib import admin
from .models import Room_Resources

@admin.register(Room_Resources)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'capacity', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'location']
