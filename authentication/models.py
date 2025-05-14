"""
This module contains the models for the authentication application.

The included models are:
    - Notification
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Since the User model from Django is being used,
# there's no need to put a User model here

class Notification(models.Model):
    """
    Model for the notification system. This model is used to store notifications for users.

    Attributes:
        is_read (models.BooleanField): A boolean field to indicate if the notification has been 
            read or not.
        subject (models.CharField): The subject of the notification.
        message (models.TextField): The message of the notification.
        timestamp (models.DateTimeField): The timestamp of when the notification was created.
        user (models.ForeignKey): A foreign key to the User model to indicate which user the 
            notification is for.

    Methods:
        `__str__`: Returns a string representation of the notification, including the timestamp and
            subject.
    """
    is_read = models.BooleanField(default=False)
    subject = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """
        Returns a string representation of the notification, inluding the timestamp and subject.
        
        The timestamp is converted to the local timezone (EST) before formatting.
        The format of the timestamp is "YYYY-MM-DD HH:MM:SS AM/PM".

        Returns:
            str: The string representation of the Notification object.
        """
        # NOTE: The timestamp is stored in UTC in the database.
        # The first line takes the timestamp and converts it to EST.
        # This is because Django doesn't automatically convert the timestamp here.
        local_timestamp = timezone.localtime(self.timestamp)
        formatted_timestamp = local_timestamp.strftime("%Y-%m-%d %I:%M:%S %p")
        return f'{formatted_timestamp} | For {self.user}: "{self.subject}"'
