from django.test import Client, TestCase 
from django.urls import reverse
import time_machine
import datetime

from django.contrib.auth.models import User, Group
from authentication.models import Notification


class DatabaseLoginViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up test data for DatabaseLoginViewTests
        # [ ]: Create a user for logging in 

###################################################################################################
# Tests for the Views for the Notification Model ##################################################
###################################################################################################
class NotificationViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up for NotificationViewTests
        # [x]: Create a user for any group
        # [ ]: Bulk create notifications for the user as well as ones not for the user
        
        notifications = [
            
        ]        
        Notification.objects.bulk_create(notifications)
        cls.notifications_url = reverse("authentication:notifications")
        
        cls.superuser_group = Group.objects.get(name="Superuser")
        
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(cls.superuser_group)
        
        cls.client = Client()
        
        
    def test_notification_view_GET_authenticated(self):
        """
        
        """
        # TODO; test_notification_view_GET_authenticated
        
    