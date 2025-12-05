from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('donor', 'Blood Donor'),
        ('recipient', 'Blood Recipient'),
        ('doctor', 'Doctor'),
        ('admin', 'Administrator'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='donor')
    phone_number = models.CharField(max_length=15, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"