from django.db import models
from users.models import User
from rooms.models import Resource

class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='bookings')
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['resource', 'starts_at', 'ends_at']), 
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking by {self.user.email} for {self.resource.name} ({self.status})"


class FileUpload(models.Model):
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploads')
    path = models.CharField(max_length=255)
    size_bytes = models.PositiveIntegerField()
    mime = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File by {self.owner_user.email} ({self.mime}, {self.size_bytes} bytes)"


class AuditLog(models.Model):
    actor_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=255)
    entity = models.CharField(max_length=100)
    entity_id = models.IntegerField()
    meta = models.JSONField(default=dict)
    ts = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actor_user.email} - {self.action} ({self.entity})"
