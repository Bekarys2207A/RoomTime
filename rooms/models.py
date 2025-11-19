from django.db import models

class Resource(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    file_path = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.location})"
