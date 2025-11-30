from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from ..serializers.room_resources import ResourceSerializer
from ..services import room_resources as resource_service


class RoomResourceViewSet(viewsets.ViewSet):
    """
    ViewSet for Room Resources CRUD operations.
    
    List/Retrieve: Public access
    Create/Update/Delete: Admin only
    
    Query Parameters for list:
    - is_active: boolean (default: true)
    - location: string (partial match)
    - capacity: integer (minimum capacity)
    """
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:  # create, update, partial_update, destroy
            permission_classes = [permissions.IsAdminUser]
        
        return [permission() for permission in permission_classes]
    
    # GET /api/resources/
    def list(self, request):
        """Get filtered list of room resources."""
        resources = resource_service.get_filtered_resources(request)
        serializer = ResourceSerializer(resources, many=True)
        return Response(serializer.data)
    
    # GET /api/resources/{pk}/
    def retrieve(self, request, pk=None):
        """Get single room resource."""
        resource = resource_service.get_resource(pk)
        if resource:
            serializer = ResourceSerializer(resource)
            return Response(serializer.data)
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # POST /api/resources/
    def create(self, request):
        """Create new room resource."""
        serializer = ResourceSerializer(data=request.data)
        if serializer.is_valid():
            resource = resource_service.add_resource(serializer.validated_data)
            return Response(
                ResourceSerializer(resource).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # PUT/PATCH /api/resources/{pk}/
    def update(self, request, pk=None):
        """Update existing room resource."""
        serializer = ResourceSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            resource = resource_service.edit_resource(pk, serializer.validated_data)
            if resource:
                return Response(ResourceSerializer(resource).data)
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # DELETE /api/resources/{pk}/
    def destroy(self, request, pk=None):
        """Delete room resource."""
        success = resource_service.remove_resource(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
