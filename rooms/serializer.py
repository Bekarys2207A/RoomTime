from rest_framework import serializers
from .models import Resource

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'name', 'location', 'capacity', 'file_path', 'is_active']
        read_only_fields = ['id']