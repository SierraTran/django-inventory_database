from django.test import Client, TestCase, tag 
from django.urls import reverse
import time_machine
import datetime

from django.contrib.auth.models import User, Group
from authentication.models import Notification


class DatabaseLoginViewTests(TestCase):
    # TODO: DatabaseLoginViewTests
    # [ ]: test_login_invalid_username
    # [ ]: test_login_invalid_password
    # [ ]: test_login_success
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up test data for DatabaseLoginViewTests
        # [ ]: Create a user for logging in 
        
    def test_login_invalid_username(self):
        """
        An error message displays for an invalid username
        """
        
    def test_login_invalid_password(self):
        """
        An error message displays for an invalid password
        """
        
    def test_login_success(self):
        """
        Successfully login and redirect to the home page
        """

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
        
    @tag("critical")
    def test_notification_view_GET(self):
        # TODO: test_notification_view_GET
        """
        User has access to their notification page, which only show notifications addressed to them.
        """
        # [x]: User logs in
        # [x]: Make sure status code is 200        
        login = self.client.login(username="testuser", password="password")
        self.assertTrue(login, "Login failed.")
        
        response = self.client.get(self.notifications_url)
        self.assertEqual(response.status_code, 200, "Failed to access the notifications page.")
        self.assertTemplateUsed(response, "notifications.html", "The correct template for the view is not used.")
    
    def test_notification_no_notifs(self):
        # TODO: test_notification_no_notifs
        """
        No notifications or notification badge will be shown.
        """
        # [x]: Delete all notifications from the database (We only need to do this for this test.)
        # [ ]: Log in and access the notification page
        # [ ]: Check for no notifications and a message that says so
        # [ ]: Make sure the notification badge doesn't show
        Notification.objects.all().delete()
        
        self.client.login(username="testuser", password="password")
        
        
        
        
    def test_notification_all_unread_notifs(self):
        # TODO: test_notification_all_unread_notifs
        """
        All notifications are shown in bold, and the notification badge is shown with the number of unread notifications.
        """
        # [ ]: Log in and access the notification page
        # [ ]: Check for notifications (all should be bold)
        # [ ]: Make sure the notification badge shows with the correct number of unread notifications
        
        
    def test_notification_all_read_notifs(self):
        # TODO: test_notification_all_read_notifs
        """
        All notifications are not shown in bold, and the notification badge won't be shown.
        """
        # [ ]: Mark all notifications as read
        # [ ]: Log in and access the notification page
        # [ ]: Check for notifications (none should be bold)
        # [ ]: Make sure the notification badge doesn't show
        
    def test_notification_read_and_unread_notifs(self):
        # TODO: test_notification_read_and_unread_notifs
        """
        Unread notifications are shown in bold while read notifications are not in bold. The notification badge will only count unread notifications.
        """
        # [ ]: Mark some notifications as read
        # [ ]: Log in and access the notification page
        # [ ]: Check for unread notifications (shown in bold) and read notifications (now shown in bold)
        # [ ]: Make sure the notification badge shows with the correct number of unread notifications
    