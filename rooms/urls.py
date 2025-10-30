from django.urls import path
from .views import ResourceListCreateAPIView, ResourceRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('', ResourceListCreateAPIView.as_view(), name='resource-list-create'),
    path('<int:pk>/', ResourceRetrieveUpdateDestroyAPIView.as_view(), name='resource-detail-update-delete'),
]
