from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usertype = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.user.username