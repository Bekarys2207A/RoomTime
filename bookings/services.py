from django.db import transaction
from .models import Booking

@transaction.atomic
def create_booking(user, validated_data):
    
    validated_data['user'] = user
    booking = Booking.objects.create(**validated_data)
    return booking
