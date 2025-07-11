from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from accounts.managers import CustomUserManager
# Create your models here.

class CustomUser(AbstractBaseUser, PermissionsMixin):
    auth0_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    profile_picture = models.URLField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    prefernce = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    Role_CHOICES = (
        ('customer','Customer'),
        ('owner', 'Owner'),
    )
    role = models.CharField(max_length=20, choices=Role_CHOICES, default='customer')
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'auth0_id'
    REQUIRED_FIELDS = ['email','role']
    def __str__(self):
        return self.email
    

    def get_full_name(self):
        return self.name if self.name else self.email