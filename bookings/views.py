from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Booking
from .serializers import BookingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        resource = request.data.get('resource')
        starts_at = request.data.get('starts_at')
        ends_at = request.data.get('ends_at')

        if not (resource and starts_at and ends_at):
            return Response(
                {"error": "Необходимо указать resource, starts_at и ends_at"},
                status=status.HTTP_400_BAD_REQUEST
            )

        overlapping = Booking.objects.filter(
            resource=resource,
            starts_at__lt=ends_at,
            ends_at__gt=starts_at
        ).exists()

        if overlapping:
            return Response(
                {"error": "Этот ресурс уже забронирован на выбранное время."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)

