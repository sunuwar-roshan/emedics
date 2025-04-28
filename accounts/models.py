from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    # is_doctor = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True, null=True)
    street_address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='profile_pictures/', blank=True, null=True) 
    # Doctor-specific fields
    specialization = models.CharField(max_length=100, blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)

    # Patient-specific fields
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=(('male', 'Male'), ('female', 'Female'), ('other', 'Other')), blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=15, blank=True, null=True)

    # "password2=confirm password field"
    # "password1=1st password field" yo duitai django user bata aauxa
    def __str__(self):
        return self.username
