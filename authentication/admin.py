from django.contrib import admin

from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["is_read"]}),
        ("Content", {"fields": ["subject", "message"]}),
        ("Recipient", {"fields": ["user"]})
    ]
    ordering = ["-timestamp"]


# Register your models here.
admin.site.register(Notification, NotificationAdmin)
