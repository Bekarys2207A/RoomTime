from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('users.urls', namespace='users')),  # namespaced
    path('admin/', admin.site.urls),
    path('resources/', include('rooms.urls')),
]