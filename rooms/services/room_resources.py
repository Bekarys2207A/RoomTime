from ..repositories import room_resources as repo


def get_filtered_resources(request):
    """Get filtered list of room resources based on query parameters."""
    queryset = repo.get_all_resources()
    
    # Parse and apply is_active filter
    is_active_param = request.query_params.get('is_active')
    queryset = _apply_active_filter(queryset, is_active_param)
    
    # Apply location filter
    location = request.query_params.get('location')
    if location:
        queryset = repo.filter_by_location(queryset, location)
    
    # Apply capacity filter
    capacity_param = request.query_params.get('capacity')
    if capacity_param:
        try:
            capacity = int(capacity_param)
            queryset = repo.filter_by_capacity(queryset, capacity)
        except (TypeError, ValueError):
            pass  # Invalid capacity, skip filter
    
    return queryset


def get_resource(resource_id):
    """Get single resource by ID."""
    return repo.get_resource(resource_id)


def add_resource(validated_data):
    """Create new room resource."""
    return repo.create_resource(validated_data)


def edit_resource(resource_id, validated_data):
    """Update existing resource."""
    resource = repo.get_resource(resource_id)
    if resource:
        updated = repo.update_resource(resource, validated_data)
        return updated
    return None


def remove_resource(resource_id):
    """Delete resource."""
    resource = repo.get_resource(resource_id)
    if resource:
        repo.delete_resource(resource)
        return True
    return False


def _apply_active_filter(queryset, is_active_param):
    """Apply active status filter. Defaults to True if not specified."""
    if is_active_param is None:
        # Default: show only active resources
        return repo.filter_by_active(queryset, True)
    
    # Parse boolean values
    val = is_active_param.strip().lower()
    if val in ('true', '1', 'yes', 'y'):
        return repo.filter_by_active(queryset, True)
    elif val in ('false', '0', 'no', 'n'):
        return repo.filter_by_active(queryset, False)
    
    return queryset
