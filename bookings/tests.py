import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rooms.models import Resource
from bookings.models import Booking

User = get_user_model()

@pytest.mark.django_db
def test_create_booking_success():
    user = User.objects.create_user(
        username='test1',          
        email='test1@example.com', 
        password='pass123'
    )
    resource = Resource.objects.create(name='Room A', location='Location A', capacity=5)
    client = APIClient()
    client.force_authenticate(user=user)

    start = timezone.now() + timedelta(hours=1)
    end = start + timedelta(hours=2)

    response = client.post('/api/bookings/', {
        "resource": resource.id,
        "starts_at": start.isoformat(),
        "ends_at": end.isoformat()
    }, format='json')

    assert response.status_code == 201
    assert Booking.objects.filter(user=user, resource=resource).exists()

@pytest.mark.django_db
def test_booking_overlap_blocks():
    user = User.objects.create_user(
        username='test2',
        email='test2@example.com', 
        password='pass123'
    )
    resource = Resource.objects.create(name='Room B', location='Location B', capacity=3)
    
    start = timezone.now() + timedelta(days=1)
    end = start + timedelta(hours=2)
    Booking.objects.create(
        user=user, 
        resource=resource, 
        starts_at=start, 
        ends_at=end, 
        status='confirmed'
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post('/api/bookings/', {
        "resource": resource.id,
        "starts_at": (start + timedelta(minutes=30)).isoformat(),
        "ends_at": (end + timedelta(minutes=30)).isoformat()
    }, format='json')

    assert response.status_code == 400
    assert "Ресурс уже забронирован" in str(response.data)

@pytest.mark.django_db
def test_cancel_booking():
    user = User.objects.create_user(
        username='test3',
        email='test3@example.com', 
        password='pass123'
    )
    resource = Resource.objects.create(name='Room C', location='Location C', capacity=2)
    
    start = timezone.now() + timedelta(hours=1)
    end = start + timedelta(hours=2)

    booking = Booking.objects.create(
        user=user, 
        resource=resource, 
        starts_at=start, 
        ends_at=end, 
        status='confirmed'
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(f'/api/bookings/{booking.id}/cancel/')
    
    assert response.status_code == 200
    booking.refresh_from_db()
    assert booking.status == 'cancelled'

@pytest.mark.django_db
def test_resource_availability():
    user = User.objects.create_user(
        username='test4',
        email='test4@example.com', 
        password='pass123'
    )
    resource = Resource.objects.create(name='Room D', location='Location D', capacity=4)
    client = APIClient()
    client.force_authenticate(user=user)

    tomorrow = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    response = client.get(f'/api/bookings/resources/{resource.id}/availability/?date={tomorrow}')
    
    assert response.status_code == 200
    assert response.data['available'] == True
    assert response.data['resource_id'] == resource.id