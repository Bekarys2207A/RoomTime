from django.db import transaction
from rest_framework import serializers
from .models import Booking, AuditLog

@transaction.atomic
def create_booking(user, validated_data):
    resource = validated_data['resource']
    start = validated_data['starts_at']
    end = validated_data['ends_at']

    if Booking.objects.select_for_update().filter(
        resource=resource,
        starts_at__lt=end,
        ends_at__gt=start
    ).exists():
        raise serializers.ValidationError("Этот ресурс уже занят в выбранное время")

    validated_data['user'] = user
    booking = Booking.objects.create(**validated_data)

    AuditLog.objects.create(
        actor_user=user,
        action='create_booking',
        entity='Booking',
        entity_id=booking.id,
        meta={'starts_at': start.isoformat(), 'ends_at': end.isoformat()}
    )

    return booking
