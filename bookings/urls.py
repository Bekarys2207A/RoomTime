from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_bookings, name='get_bookings'),
]
