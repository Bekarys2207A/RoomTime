from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.room_resource_views import RoomResourceViewSet

router = DefaultRouter()
router.register(r'resources', RoomResourceViewSet, basename='resource')

urlpatterns = [
    path('', include(router.urls)),
]
