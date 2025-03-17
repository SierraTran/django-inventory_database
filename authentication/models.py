from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# Since the User model from Django is being used,
# there's no need to put a User model here

class Notification(models.Model):
    is_read = models.BooleanField(default=False)
    subject = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.timestamp} | For {self.user}: "{self.message}"'
    
    def mark_as_read(notification_id):
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()