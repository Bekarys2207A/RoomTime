from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_password_reset_email(user_email, link):
    send_mail(
        "RoomTime Password Reset",
        f"Click the link to reset your password:\n{link}",
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )