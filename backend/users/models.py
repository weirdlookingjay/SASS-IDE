from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    """Custom user model for the IDE platform"""
    
    # Additional fields can be added here
    is_admin = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Ensure superusers are also admins
        if self.is_superuser:
            self.is_admin = True
        super().save(*args, **kwargs)
        
    class Meta:
        ordering = ['-date_joined']
        
    def __str__(self):
        return self.username
