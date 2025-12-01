from django.db import transaction
from rest_framework import serializers
from .models import Booking, AuditLog
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from django.core.cache import cache
import redis

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

HOLD_TTL_MINUTES = 15
r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

@shared_task
def release_holds():
    now = timezone.now()
    ttl = now - timedelta(minutes=HOLD_TTL_MINUTES)

    expired = Booking.objects.filter(
        status=Booking.STATUS_PENDING,
        created_at__lt=ttl
    )

    booking_ids = list(expired.values_list("id", flat=True))
    resource_ids = list(expired.values_list("resource_id", flat=True))

    count = expired.count()

    expired.update(status=Booking.STATUS_CANCELLED)


    for b_id in booking_ids:
        r.delete(f"booking_lock:{b_id}")

    for r_id in resource_ids:
        cache_key = f"availability:{r_id}"
        cache.delete(cache_key)

    return f"Released {count} expired holds"