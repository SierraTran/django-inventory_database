"""
This module defines the admin interface for the authentication app.
It customizes the admin views for the Notification model.
"""

from django.contrib import admin
from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the Notification model.
    
    Attributes:
        fieldsets (list): Fieldsets for the admin form layout.
            - None: Default fieldset with is_read field.
            - Content: Fieldset for the notification content with subject and message fields.
            - Recipient: Fieldset for the recipient with user field.
        ordering (list): Default ordering of notifications in the list view
            - timestamp: Order reverse-chronologically by timestamp
    """
    fieldsets = [
        (None, {"fields": ["is_read"]}),
        ("Content", {"fields": ["subject", "message"]}),
        ("Recipient", {"fields": ["user"]})
    ]
    ordering = ["-timestamp"]


# Register your models here.
admin.site.register(Notification, NotificationAdmin)
