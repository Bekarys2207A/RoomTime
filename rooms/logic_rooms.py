from rest_framework.permissions import IsAdminUser, AllowAny
from .models import Room_Resources

def resource_queryset(request):
    queryset = Room_Resources.objects.all()
    is_active = request.query_params.get('is_active')
    location = request.query_params.get('location')
    capacity = request.query_params.get('capacity')

    if is_active is None:
        queryset = queryset.filter(is_active=True)
    else:
        val = is_active.strip().lower()
        if val in ('true', '1', 'yes', 'y'):
            queryset = queryset.filter(is_active=True)
        elif val in ('false', '0', 'no', 'n'):
            queryset = queryset.filter(is_active=False)

    if location is not None:
        queryset = queryset.filter(location__icontains=location)

    if capacity is not None:
        try:
            queryset = queryset.filter(capacity__gte=int(capacity))
        except (TypeError, ValueError):
            pass

    return queryset

def resource_permissions(request, action):
    permissions_by_action = {
        'list': [AllowAny],
        'create': [IsAdminUser],
        'retrieve': [AllowAny],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],
        'destroy': [IsAdminUser],
    }
    return [perm() for perm in permissions_by_action.get(action, [AllowAny])]

def get_action(request_method, detail=False):
    # Universal mapping for GenericAPIView (only two methods for ListCreate, four for RetrieveUpdateDestroy)
    mapping = {
        'GET':    'retrieve' if detail else 'list',      # For list view (override to 'retrieve' in detail view)
        'POST':   'create',
        'PUT':    'update',
        'PATCH':  'partial_update',
        'DELETE': 'destroy',
    }
    return mapping.get(request_method, None)
