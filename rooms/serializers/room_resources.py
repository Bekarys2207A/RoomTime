from rest_framework import serializers
from rooms.models import Room_Resources


class ResourceSerializer(serializers.ModelSerializer):
    """
    Serializer for Room_Resources model.
    Handles validation and serialization of room resource data.
    """
    
    class Meta:
        model = Room_Resources
        fields = ['id', 'name', 'location', 'capacity', 'file_path', 'is_active']
        read_only_fields = ['id']
    
    def validate_name(self, value):
        """Validate that name is not empty and not too short."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value.strip()
    
    def validate_location(self, value):
        """Validate that location is not empty."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Location must be at least 2 characters long.")
        return value.strip()
    
    def validate_capacity(self, value):
        """Validate that capacity is positive."""
        if value < 1:
            raise serializers.ValidationError("Capacity must be at least 1.")
        if value > 10000:
            raise serializers.ValidationError("Capacity cannot exceed 10,000.")
        return value
    
    def validate(self, data):
        """
        Object-level validation.
        Perform any cross-field validation here if needed.
        """
        # Example: You can add business logic here
        # For instance, check if a location+capacity combination is valid
        return data


class ResourceListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing resources.
    Excludes file_path for performance.
    """
    
    class Meta:
        model = Room_Resources
        fields = ['id', 'name', 'location', 'capacity', 'is_active']


class ResourceCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating resources.
    Makes file_path optional.
    """
    
    file_path = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = Room_Resources
        fields = ['name', 'location', 'capacity', 'file_path', 'is_active']
    
    def validate_name(self, value):
        """Validate that name is not empty."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value.strip()
    
    def validate_location(self, value):
        """Validate that location is not empty."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Location must be at least 2 characters long.")
        return value.strip()
    
    def validate_capacity(self, value):
        """Validate that capacity is positive."""
        if value < 1:
            raise serializers.ValidationError("Capacity must be at least 1.")
        if value > 10000:
            raise serializers.ValidationError("Capacity cannot exceed 10,000.")
        return value
