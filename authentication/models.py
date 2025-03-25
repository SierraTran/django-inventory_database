# TODO: Module docstring
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

# Since the User model from Django is being used,
# there's no need to put a User model here

class Notification(models.Model):
    # TODO: Class docstring
    is_read = models.BooleanField(default=False)
    subject = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        local_timestamp = timezone.localtime(self.timestamp) 
        formatted_timestamp = local_timestamp.strftime("%Y-%m-%d %I:%M:%S %p")
        return f'{formatted_timestamp} | For {self.user}: "{self.subject}"'