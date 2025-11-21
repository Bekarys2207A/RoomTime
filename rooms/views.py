from rest_framework import generics, permissions
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import Resource
from .serializer import ResourceSerializer


# List & Filter resources
class ResourceListCreateAPIView(generics.ListCreateAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    permission_classes_by_action = {
        'list': [AllowAny],
        'create': [IsAdminUser],
    }

    def get_permissions(self):
        # Для GenericAPIView без ViewSet определяем action по методу
        action = getattr(self, 'action', None)
        if action is None:
            method = self.request.method
            if method == 'GET':
                action = 'list'
            elif method == 'POST':
                action = 'create'
        perms = self.permission_classes_by_action.get(action, [AllowAny])
        return [perm() for perm in perms]

    def get_queryset(self):
        queryset = Resource.objects.all()
        is_active = self.request.query_params.get('is_active')
        location = self.request.query_params.get('location')
        capacity = self.request.query_params.get('capacity')

        if is_active is not None:
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


# Retrieve/Update/Delete a resource
class ResourceRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    permission_classes_by_action = {
        'retrieve': [AllowAny],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],
        'destroy': [IsAdminUser],
    }

    def get_permissions(self):
        action = getattr(self, 'action', None)
        if action is None:
            method = self.request.method
            if method == 'GET':
                action = 'retrieve'
            elif method == 'PUT':
                action = 'update'
            elif method == 'PATCH':
                action = 'partial_update'
            elif method == 'DELETE':
                action = 'destroy'
        perms = self.permission_classes_by_action.get(action, [AllowAny])
        return [perm() for perm in perms]
