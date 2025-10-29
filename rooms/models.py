from django.db import models

class Resource(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    file_path = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.location})"


# class TimeSlot(models.Model):
#     STATUS_CHOICES = (
#         ('available', 'Available'),
#         ('held', 'Held'),
#         ('booked', 'Booked'),
#     )

#     resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='time_slots')
#     starts_at = models.DateTimeField()
#     ends_at = models.DateTimeField()
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')

#     class Meta:
#         indexes = [
#             models.Index(fields=['resource', 'starts_at']),
#             models.Index(fields=['starts_at', 'ends_at']),
#         ]
#         ordering = ['starts_at']

#     def __str__(self):
#         return f"{self.resource.name} | {self.starts_at} - {self.ends_at} [{self.status}]"
