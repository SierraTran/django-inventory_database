from django.contrib import admin

from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    ordering = ["timestamp"]
    
    
# Register your models here.
admin.site.register(Notification, NotificationAdmin)