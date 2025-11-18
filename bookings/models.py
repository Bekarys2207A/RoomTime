from django.db import models
from users.models import User
from rooms.models import Resource

# Create your models here.

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking by {self.user.email} for {self.resource.name} ({self.status})"    
    

class FileUpload(models.Model):
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=255)
    size_bytes = models.PositiveIntegerField()
    mime = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"FileUpload by {self.owner_user.email} - {self.path}"


class AuditLog(models.Model):
    actor_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=255)
    entity = models.CharField(max_length=100)
    entity_id = models.IntegerField()
    meta = models.JSONField(default=dict)
    ts = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.actor_user.email} - {self.action} ({self.entity})"