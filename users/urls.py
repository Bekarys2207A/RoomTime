from django.urls import path, include
from .views import Register, home

app_name = 'users'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('register/', Register.as_view(), name='register'),
    path('home/', home, name='home'),
]