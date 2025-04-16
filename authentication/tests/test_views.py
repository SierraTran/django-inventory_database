from django.test import Client, TestCase, tag 
from django.urls import reverse

from django.contrib.auth.models import User, Group
from authentication.models import Notification


class HomeViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up test data for HomeViewTests
        # [x]: Create a user for logging in
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(cls.superuser_group)
        

class DatabaseLoginViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up test data for DatabaseLoginViewTests
        # [x]: Create a user for logging in 
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(cls.superuser_group)
        
    def test_login_invalid_username(self):
        """
        An error message displays for an invalid username
        """
        # TODO: test_login_invalid_username
        # [ ]: Attempt to log in with an invalid username
        # [ ]: Check for an error message
        # [ ]: Make sure the user is not logged in
        
    def test_login_invalid_password(self):
        """
        An error message displays for an invalid password
        """
        # TODO: test_login_invalid_password
        # [ ]: Attempt to log in with an invalid password 
        # [ ]: Check for an error message
        # [ ]: Make sure the user is not logged in
        
    def test_login_success(self):
        """
        Successfully login and redirect to the home page
        """
        # TODO: test_login_success

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
        
        cls.user1 = User.objects.create_user(username="testuser1", password="password")
        cls.user1.groups.add(cls.superuser_group)
        
        cls.client = Client()
        
    @tag("critical")
    def test_notification_view_GET(self):
        """
        User has access to their notification page, which only show notifications addressed to them.
        """      
        login = self.client.login(username="testuser1", password="password")
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
        # [x]: Log in and access the notification page
        # [ ]: Check for no notifications and a message that says so
        # [ ]: Make sure the notification badge doesn't show
        Notification.objects.all().delete()
        
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.notifications_url)
        self.assertEqual(response.status_code, 200, "Failed to access the notifications page.")
        
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


class NotificationUpdateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up test data for NotificationUpdateViewTests
        # [ ]: Create a notification to update
        # [ ]: Create two users: one with access to the notification and one without access
        
        cls.client = Client()
        
    @tag("critical")
    def test_notification_update_view_access_control(self):
        """
        Access control for the notification update view.
        """
        # TODO: test_notification_update_view_access_control
        # [ ]: Log in as the user with access to the notification
        # [ ]: Make sure the user can access the notification update view   
        # [ ]: Log in as the user without access to the notification
        # [ ]: Make sure the user cannot access the notification update view

    def test_get_context_data(self):
        """
        Test the context data for the notification update view.
        """
        # TODO: test_get_context_data
        # [ ]: Log in as the user with access to the notification
        # [ ]: Make a GET request to the notification update view


class NotificationDeleteViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up for NotificationDeleteViewTests
        # [ ]: Create a notification to delete
        # [ ]: Create two users: one with access to the notification and one without access
        
    def test_notification_delete_view_access_control(self):
        """
        Test the access control for the notification delete view.
        """
        # TODO: test_notification_delete_view_access_control
        # [ ]: Log in as the user without access to the notification
        # [ ]: Make sure the user can't access the view or delete the notification
        # [ ]: Log in as the user with access to the notification
        # [ ]: Make sure the user can access the view and delete the notification
        
    def test_post_cancel_delete(self):
        """
        Test the cancel delete functionality for the notification delete view.
        """
        # TODO: test_post_cancel_delete
        # [ ]: Log in as the user that can access the view and delete the notification
        
    def test_post_confirm_delete(self):
        """
        Test the confirm delete functionality for the notification delete view.
        """
        # TODO: test_post_confirm_delete
        # [ ]: Log in as the user that can access the view and delete the notification
