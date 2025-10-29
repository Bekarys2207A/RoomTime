from rest_framework import generics, permissions
from .models import Resource
from .serializer import ResourceSerializer

# List & Filter resources
class ResourceListCreateAPIView(generics.ListCreateAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    
    def get_queryset(self):
        queryset = Resource.objects.all()
        is_active = self.request.query_params.get('is_active')
        location = self.request.query_params.get('location')
        capacity = self.request.query_params.get('capacity')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if location is not None:
            queryset = queryset.filter(location__icontains=location)
        if capacity is not None:
            queryset = queryset.filter(capacity__gte=capacity)
        return queryset
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

# Retrieve/Update/Delete a resource
class ResourceRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]