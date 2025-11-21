from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, resource_availability

router = DefaultRouter()
router.register(r'', BookingViewSet, basename='bookings')

urlpatterns = [
    path('resources/<int:resource_id>/availability/', resource_availability, name='resource-availability'),
] + router.urls