from rest_framework import generics
from .serializer import ResourceSerializer
from .models import Room_Resources
from .logic_rooms import resource_queryset, resource_permissions, get_action

# List & Filter resources
class ResourceListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ResourceSerializer

    def get_permissions(self):
        action = get_action(self.request.method)
        return resource_permissions(self.request, action)

    def get_queryset(self):
        return resource_queryset(self.request)

# Retrieve/Update/Delete a resource
class ResourceRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResourceSerializer

    def get_permissions(self):
        action = get_action(self.request.method, detail=True)
        return resource_permissions(self.request, action)

    def get_queryset(self):
        # В логике на детальное представление чаще всего возвращают все объекты
        return Room_Resources.objects.all()
