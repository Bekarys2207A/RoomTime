from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = ['id', 'user', 'resource', 'starts_at', 'ends_at', 'status', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate(self, data):

        start = data.get('starts_at')
        end = data.get('ends_at')
        resource = data.get('resource')

        if not start or not end:
            raise serializers.ValidationError("Поля 'starts_at' и 'ends_at' обязательны.")
        if not resource:
            raise serializers.ValidationError("Поле 'resource' обязательно.")

        if start >= end:
            raise serializers.ValidationError("Время окончания должно быть позже времени начала.")

        overlap = (
            Booking.objects.filter(resource=resource, starts_at__lt=end, ends_at__gt=start)
            .exclude(pk=getattr(self.instance, 'pk', None))  # исключаем саму себя при update
            .exists()
        )

        if overlap:
            raise serializers.ValidationError("Ресурс уже забронирован в этот интервал времени.")

        return data
