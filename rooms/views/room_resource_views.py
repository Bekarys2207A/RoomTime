from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Импортируем ВСЕ ваши сериализаторы
from ..serializers.room_resources import (
    ResourceSerializer, 
    ResourceListSerializer, 
    ResourceCreateUpdateSerializer
)
from ..services import room_resources as resource_service

error_responses = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden - Admin access required",
    404: "Not Found"
}

class RoomResourceViewSet(viewsets.ViewSet):
    """
    ViewSet for Room Resources CRUD operations.
    """
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @swagger_auto_schema(
        tags=["Resources"],
        operation_summary="List all room resources",
        manual_parameters=[
            openapi.Parameter('is_active', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, default=True),
            openapi.Parameter('location', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('capacity', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ],
        # 👇 Используем легкий сериализатор для списка
        responses={200: ResourceListSerializer(many=True)}
    )
    def list(self, request):
        resources = resource_service.get_filtered_resources(request)
        serializer = ResourceListSerializer(resources, many=True) # <-- Тут тоже меняем
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=["Resources"],
        operation_summary="Retrieve a resource",
        responses={200: ResourceSerializer(), 404: "Not Found"}
    )
    def retrieve(self, request, pk=None):
        resource = resource_service.get_resource(pk)
        if resource:
            serializer = ResourceSerializer(resource)
            return Response(serializer.data)
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        tags=["Resources"],
        operation_summary="Create a new resource",
        # 👇 Используем сериализатор для создания (без id)
        request_body=ResourceCreateUpdateSerializer, 
        responses={201: ResourceSerializer(), **error_responses}
    )
    def create(self, request):
        serializer = ResourceCreateUpdateSerializer(data=request.data) # <-- И тут
        if serializer.is_valid():
            resource = resource_service.add_resource(serializer.validated_data)
            return Response(ResourceSerializer(resource).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=["Resources"],
        operation_summary="Update a resource",
        # 👇 Используем сериализатор для обновления
        request_body=ResourceCreateUpdateSerializer,
        responses={200: ResourceSerializer(), **error_responses}
    )
    def update(self, request, pk=None):
        serializer = ResourceCreateUpdateSerializer(data=request.data, partial=True) # <-- И тут
        if serializer.is_valid():
            resource = resource_service.edit_resource(pk, serializer.validated_data)
            if resource:
                return Response(ResourceSerializer(resource).data)
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=["Resources"],
        operation_summary="Delete a resource",
        responses={204: "No Content", **error_responses}
    )
    def destroy(self, request, pk=None):
        success = resource_service.remove_resource(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
