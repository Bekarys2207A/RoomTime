from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime

from .models import Booking
from .serializers import BookingSerializer
from .services import create_booking
from rooms.models import Resource

class BookingViewSet(viewsets.ModelViewSet):

    queryset = Booking.objects.all().order_by('-starts_at')
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['starts_at', 'ends_at', 'created_at']
    search_fields = ['resource__name', 'user__email']

    def perform_create(self, serializer):
        create_booking(self.request.user, serializer.validated_data)

    def get_queryset(self):

        qs = super().get_queryset()
        resource_id = self.request.query_params.get('resource')
        mine = self.request.query_params.get('mine')

        if resource_id:
            qs = qs.filter(resource_id=resource_id)
        if mine and mine.lower() in ('1', 'true', 'yes'):
            qs = qs.filter(user=self.request.user)
        return qs

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        
        if booking.user != request.user:
            return Response(
                {"error": "Вы можете отменять только свои бронирования"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.status == 'cancelled':
            return Response(
                {"error": "Бронирование уже отменено"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.save()
        
        return Response({
            "message": "Бронирование успешно отменено",
            "booking_id": booking.id,
            "status": booking.status
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resource_availability(request, resource_id):

    date_str = request.GET.get('date')
    if not date_str:
        return Response({"error": "Параметр date обязателен (YYYY-MM-DD)"}, status=400)
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response({"error": "Неверный формат даты. Используйте YYYY-MM-DD"}, status=400)

    try:
        resource = Resource.objects.get(pk=resource_id, is_active=True)
    except Resource.DoesNotExist:
        return Response({"error": "Ресурс не найден или неактивен"}, status=404)

    start_of_day = timezone.make_aware(datetime.combine(date_obj, datetime.min.time()))
    end_of_day = timezone.make_aware(datetime.combine(date_obj, datetime.max.time()))

    busy_slots = Booking.objects.filter(
        resource=resource,
        starts_at__lt=end_of_day,
        ends_at__gt=start_of_day,
        status__in=['pending', 'confirmed'] 
    ).order_by('starts_at')

    busy_intervals = [
        {
            "starts_at": slot.starts_at,
            "ends_at": slot.ends_at,
            "status": slot.status
        }
        for slot in busy_slots
    ]

    return Response({
        "resource_id": resource_id,
        "resource_name": resource.name,
        "date": date_str,
        "available": len(busy_intervals) == 0,
        "busy_slots": busy_intervals
    })