from rooms.models import Room_Resources


def get_all_resources():
    """Get all room resources."""
    return Room_Resources.objects.all()


def get_resource(resource_id):
    """Get single resource by ID."""
    try:
        return Room_Resources.objects.get(pk=resource_id)
    except Room_Resources.DoesNotExist:
        return None


def filter_by_active(queryset, is_active):
    """Filter resources by active status."""
    return queryset.filter(is_active=is_active)


def filter_by_location(queryset, location):
    """Filter resources by location (case-insensitive)."""
    return queryset.filter(location__icontains=location)


def filter_by_capacity(queryset, min_capacity):
    """Filter resources by minimum capacity."""
    return queryset.filter(capacity__gte=min_capacity)


def create_resource(data):
    """Create new room resource."""
    return Room_Resources.objects.create(**data)


def update_resource(resource, data):
    """Update existing resource."""
    for key, value in data.items():
        setattr(resource, key, value)
    resource.save()
    return resource


def delete_resource(resource):
    """Delete resource."""
    resource.delete()
