from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Since the User model from Django is being used,
# there's no need to put a User model here

class Notification(models.Model):
    is_read = models.BooleanField(default=False)
    messgae = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)