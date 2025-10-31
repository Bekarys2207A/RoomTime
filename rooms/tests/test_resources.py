import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rooms.models import Resource

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def sample_resources(db):
    Resource.objects.create(name="Room A", location="Almaty", capacity=10, is_active=True)
    Resource.objects.create(name="Room B", location="Taldykorgan", capacity=5, is_active=False)
    Resource.objects.create(name="Room C", location="Astana", capacity=7, is_active=True)

@pytest.mark.django_db
def test_filter_by_is_active(api_client, sample_resources):
    url = reverse('resource-list-create')
    response = api_client.get(url, {'is_active': 'true'})
    assert response.status_code == 200
    assert all(resource['is_active'] for resource in response.data)
    assert len(response.data) == 2  # Only Room A and Room C are active

@pytest.mark.django_db
def test_filter_by_location(api_client, sample_resources):
    url = reverse('resource-list-create')
    response = api_client.get(url, {'location': 'Almaty'})
    assert response.status_code == 200
    assert all(resource['location'] == 'Almaty' for resource in response.data)
    assert len(response.data) == 1  

@pytest.mark.django_db
def test_filter_by_capacity(api_client, sample_resources):
    url = reverse('resource-list-create')
    response = api_client.get(url, {'capacity': 7})
    assert response.status_code == 200
    assert all(resource['capacity'] >= 7 for resource in response.data)
    assert len(response.data) == 2  # Room A (10) and Room C (7) meet the condition
