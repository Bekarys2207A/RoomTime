from rest_framework import serializers
from .models import Room_Resources

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room_Resources
        fields = ['id', 'name', 'location', 'capacity', 'file_path', 'is_active']
        read_only_fields = ['id']