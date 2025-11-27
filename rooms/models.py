from django.db import models

<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
class Room_Resources(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    capacity = models.IntegerField()
    file_path = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.location})"


class TimeSlot(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('held', 'Held'),
        ('booked', 'Booked'),
    ]
    
    resource = models.ForeignKey(Room_Resources, on_delete=models.CASCADE)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    class Meta:
        indexes = [
            models.Index(fields=['resource', 'starts_at']),
            models.Index(fields=['starts_at', 'ends_at']),
        ]
        ordering = ['starts_at']

    def __str__(self):
        return f"{self.resource.name} | {self.starts_at} - {self.ends_at} [{self.status}]"
