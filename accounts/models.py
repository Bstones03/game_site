from django.db import models

from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(default=100.00, max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username}'s Profile"

