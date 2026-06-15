from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
from django.utils import timezone


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    email_confirmed = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.username


class Confirm(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="confirmation")
    otp = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}-{self.otp}"

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)