# tests.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .models import Resource
from .serializer import ResourceSerializer


@pytest.mark.django_db
class TestResourceModel:
    def test_str_representation(self):
        resource = Resource.objects.create(
            name="Room 101",
            location="Building A",
            capacity=10,
            file_path="/files/room101.pdf",
            is_active=True,
        )
        assert str(resource) == "Room 101 (Building A)"


@pytest.mark.django_db
class TestResourceSerializer:
    def test_serializer_fields(self):
        resource = Resource.objects.create(
            name="Room 102",
            location="Building B",
            capacity=20,
            file_path="/files/room102.pdf",
            is_active=False,
        )
        data = ResourceSerializer(resource).data
        # проверяем, что все поля на месте
        assert set(data.keys()) == {"id", "name", "location", "capacity", "file_path", "is_active"}
        # id только для чтения – при входных данных он должен игнорироваться
        serializer = ResourceSerializer(
            data={
                "id": 999,
                "name": "Room 103",
                "location": "Building C",
                "capacity": 30,
                "file_path": "/files/room103.pdf",
                "is_active": True,
            }
        )
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        # id не должен быть 999
        assert instance.id != 999
        assert instance.name == "Room 103"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def resource_factory():
    def _factory(**kwargs):
        defaults = {
            "name": "Default Room",
            "location": "Default Building",
            "capacity": 10,
            "file_path": "/files/default.pdf",
            "is_active": True,
        }
        defaults.update(kwargs)
        return Resource.objects.create(**defaults)

    return _factory


@pytest.mark.django_db
class TestResourceListCreateAPIView:
    def test_list_resources(self, api_client, resource_factory):
        r1 = resource_factory(name="Room A", location="Loc1", is_active=True, capacity=10)
        r2 = resource_factory(name="Room B", location="Loc2", is_active=False, capacity=5)

        url = reverse("resource-list-create")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # проверяем, что вернулись оба объекта
        returned_ids = {item["id"] for item in response.data}
        assert {r1.id, r2.id}.issubset(returned_ids)

    def test_filter_is_active_true(self, api_client, resource_factory):
        active = resource_factory(is_active=True)
        resource_factory(is_active=False)

        url = reverse("resource-list-create")
        response = api_client.get(url, {"is_active": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == active.id

    def test_filter_is_active_false(self, api_client, resource_factory):
        resource_factory(is_active=True)
        inactive = resource_factory(is_active=False)

        url = reverse("resource-list-create")
        response = api_client.get(url, {"is_active": "false"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == inactive.id

    def test_filter_location_icontains(self, api_client, resource_factory):
        r1 = resource_factory(location="Almaty City")
        resource_factory(location="Astana")

        url = reverse("resource-list-create")
        response = api_client.get(url, {"location": "alma"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == r1.id

    def test_filter_capacity_gte(self, api_client, resource_factory):
        small = resource_factory(capacity=5)
        big = resource_factory(capacity=20)

        url = reverse("resource-list-create")
        response = api_client.get(url, {"capacity": "10"})

        assert response.status_code == status.HTTP_200_OK
        ids = {item["id"] for item in response.data}
        assert big.id in ids
        assert small.id not in ids

    def test_filter_capacity_invalid_value_ignored(self, api_client, resource_factory):
        r1 = resource_factory(capacity=5)
        r2 = resource_factory(capacity=20)

        url = reverse("resource-list-create")
        response = api_client.get(url, {"capacity": "not-int"})

        assert response.status_code == status.HTTP_200_OK
        ids = {item["id"] for item in response.data}
        assert {r1.id, r2.id}.issubset(ids)

    def test_create_resource_requires_admin(self, api_client):
        url = reverse("resource-list-create")
        payload = {
            "name": "New Room",
            "location": "New Building",
            "capacity": 15,
            "file_path": "/files/new.pdf",
            "is_active": True,
        }
        # без прав админа должен быть 403
        response = api_client.post(url, payload, format="json")
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
class TestResourceRetrieveUpdateDestroyAPIView:
    def test_retrieve_resource(self, api_client, resource_factory):
        resource = resource_factory()
        # ВАЖНО: ваш urls.py сейчас path('/') – обычно надо path('<int:pk>/')
        # ниже предполагается, что вы поправите urls.py:
        # path('<int:pk>/', ResourceRetrieveUpdateDestroyAPIView.as_view(), name='resource-detail-update-delete')
        url = reverse("resource-detail-update-delete", kwargs={"pk": resource.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == resource.id

    def test_update_requires_admin(self, api_client, resource_factory):
        resource = resource_factory(name="Old name")
        url = reverse("resource-detail-update-delete", kwargs={"pk": resource.id})

        response = api_client.put(
            url,
            {
                "name": "New name",
                "location": resource.location,
                "capacity": resource.capacity,
                "file_path": resource.file_path,
                "is_active": resource.is_active,
            },
            format="json",
        )
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    def test_delete_requires_admin(self, api_client, resource_factory):
        resource = resource_factory()
        url = reverse("resource-detail-update-delete", kwargs={"pk": resource.id})

        response = api_client.delete(url)
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
