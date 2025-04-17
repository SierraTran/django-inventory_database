from django.test import Client, TestCase, tag 
from django.urls import reverse
from django.utils import timezone

from django.contrib.auth.models import User, Group
from freezegun import freeze_time
from authentication.models import Notification

import datetime


class HomeViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up test data for HomeViewTests
        # [x]: Create a user for logging in
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.superuser = Group.objects.get(name="Superuser")
        cls.user.groups.add(cls.superuser_group)
        cls.client = Client()
        

class DatabaseLoginViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up test data for DatabaseLoginViewTests
        # [x]: Create a user for logging in 
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(Group.objects.get(name="Superuser"))
        cls.client = Client()
        
    def test_login_invalid_username(self):
        """
        An error message displays for an invalid username
        """
        # TODO: test_login_invalid_username
        # [ ]: Attempt to log in with an invalid username
        # [ ]: Check for an error message
        # [ ]: Make sure the user is not logged in
        response = self.client.login(username="invalid", password="password")
        
        
    def test_login_invalid_password(self):
        """
        An error message displays for an invalid password
        """
        # TODO: test_login_invalid_password
        # [ ]: Attempt to log in with an invalid password 
        # [ ]: Check for an error message
        # [ ]: Make sure the user is not logged in
        response = self.client.login(username="testuser", password="invalid")
        
    def test_login_success(self):
        """
        Successfully login and redirect to the home page
        """
        # TODO: test_login_success
        response = self.client.login(username="testuser", password="password")
        

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
        
        login = self.client.login(username="testuser1", password="password")
        self.assertTrue(login, "Login failed.")
        
        response = self.client.get(self.notifications_url)
        self.assertEqual(response.status_code, 200, "Failed to access the notifications page.")
        self.assertTemplateUsed(response, "notifications.html", "The correct template for the view is not used.")
        
    def test_notification_all_unread_notifs(self):
        # TODO: test_notification_all_unread_notifs
        """
        All notifications are shown in bold, and the notification badge is shown with the number of unread notifications.
        """
        # [x]: Log in and access the notification page
        # [ ]: Check for notifications (all should be bold)
        # [ ]: Make sure the notification badge shows with the correct number of unread notifications
        login = self.client.login(username="testuser1", password="password")
        self.assertTrue(login, "Login failed.")
        
        response = self.client.get(self.notifications_url)
        self.assertEqual(response.status_code, 200, "Failed to access the notifications page.")
        self.assertTemplateUsed(response, "notifications.html", "The correct template for the view is not used.")
        
        
    def test_notification_all_read_notifs(self):
        # TODO: test_notification_all_read_notifs
        """
        All notifications are not shown in bold, and the notification badge won't be shown.
        """
        # [ ]: Mark all notifications as read
        # [x]: Log in and access the notification page
        # [ ]: Check for notifications (none should be bold)
        # [ ]: Make sure the notification badge doesn't show
        login = self.client.login(username="testuser1", password="password")
        self.assertTrue(login, "Login failed.")
        
        response = self.client.get(self.notifications_url)
        self.assertEqual(response.status_code, 200, "Failed to access the notifications page.")
        self.assertTemplateUsed(response, "notifications.html", "The correct template for the view is not used.")
        
    def test_notification_read_and_unread_notifs(self):
        # TODO: test_notification_read_and_unread_notifs
        """
        Unread notifications are shown in bold while read notifications are not in bold. The notification badge will only count unread notifications.
        """
        # [ ]: Mark some notifications as read
        # [x]: Log in and access the notification page
        # [ ]: Check for unread notifications (shown in bold) and read notifications (now shown in bold)
        # [ ]: Make sure the notification badge shows with the correct number of unread notifications
        login = self.client.login(username="testuser1", password="password")
        self.assertTrue(login, "Login failed.")
        
        response = self.client.get(self.notifications_url)
        self.assertEqual(response.status_code, 200, "Failed to access the notifications page.")
        self.assertTemplateUsed(response, "notifications.html", "The correct template for the view is not used.")


class NotificationUpdateViewTests(TestCase):
    # NOTE: Date and time is set to January 1, 2025 at 12:00 for testing purposes
    aware_datetime = timezone.make_aware(datetime.datetime(2025, 1, 1, 12, 0, 0))
    
    @classmethod
    @freeze_time(aware_datetime)
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up test data for NotificationUpdateViewTests
        # [x]: Create two users: one with access to the notification and one without access
        # [x]: Create a notification to update
        cls.user_with_access = User.objects.create_user(username="testuser1", password="password")
        cls.user_with_no_access = User.objects.create_user(username="testuser2", password="password")
        
        Notification.objects.create(
            # is_read automatically set to false
            subject="Welcome!",
            message="Welcome to the Inventory Database.",
            # timestamp automatically set
            user=cls.user_with_access
        )        
        cls.notification = Notification.objects.filter(pk=1).first()
        cls.notification_update_url = reverse("authentication:notification_update_form", kwargs={"pk": cls.notification.pk})
        
        cls.client = Client()
        
    @tag("critical")
    def test_notification_update_view_access_control(self):
        """
        Access control for the notification update view.
        """
        # TODO: test_notification_update_view_access_control
        # [x]: Log in as the user with access to the notification
        # [x]: Make sure the user can access the notification update view   
        # [x]: Log in as the user without access to the notification
        # [x]: Make sure the user cannot access the notification update view
        self.client.login(username="testuser1", password="password")
        response = self.client.get(self.notification_update_url)        
        self.assertEqual(response.status_code, 200, "The user failed to access the update view for their notification.")
        self.client.logout()
        
        self.client.login(username="testuser2", password="password")
        response = self.client.get(self.notification_update_url)        
        self.assertEqual(response.status_code, 403, "The user unexpectedly gained access to the update view for a notification that isn't for them.")
        self.client.logout()        

    def test_get_context_data(self):
        """
        Test the context data for the notification update view.
        """
        # TODO: test_get_context_data
        # [ ]: Log in as the user with access to the notification
        # [ ]: Make a GET request to the notification update view
        self.client.login(username="testuser1", password="password")
        
    def test_update_notification(self):
        """
        Test that the notification can be updated correctly.
        """
        # TODO: test_update_notification


class NotificationDeleteViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up for NotificationDeleteViewTests
        # [x]: Create a notification to delete
        # [x]: Create two users: one with access to the notification and one without access
        cls.user_with_access = User.objects.create_user(username="testuser1", password="password")
        cls.user_with_no_access = User.objects.create_user(username="testuser2", password="password")
        
        Notification.objects.create(
            # is_read automatically set to false
            subject="Welcome!",
            message="Welcome to the Inventory Database.",
            # timestamp automatically set
            user=cls.user_with_access
        )        
        cls.notification = Notification.objects.filter(pk=1).first()
        cls.notification_delete_url = reverse("authentication:notification_confirm_delete", kwargs={"pk": cls.notification.pk})
        
        cls.client = Client()
        
    def test_notification_delete_view_access_control(self):
        """
        Test the access control for the notification delete view.
        """
        # TODO: test_notification_delete_view_access_control
        # [x]: Log in as the user without access to the notification
        # [x]: Make sure the user can't access the view or delete the notification
        # [x]: Log in as the user with access to the notification
        # [x]: Make sure the user can access the view and delete the notification
        self.client.login(username="testuser1", password="password")
        response = self.client.get(self.notification_delete_url)
        self.assertEqual(response.status_code, 200, "The user failed to access the update view for their notification.")
        self.client.logout()
        
        self.client.login(username="testuser2", password="password")
        response = self.client.get(self.notification_delete_url)        
        self.assertEqual(response.status_code, 403, "The user unexpectedly gained access to the update view for a notification that isn't for them.")
        self.client.logout()
        
    def test_post_cancel_delete(self):
        """
        Test the cancel delete functionality for the notification delete view.
        """
        # TODO: test_post_cancel_delete
        # [x]: Log in as the user that can access the view and delete the notification
        # [x]: Cancel the deletion
        # [x]: Make sure that the notification is still there
        self.client.login(username="testuser1", password="password")
        response = self.client.post(self.notification_delete_url, {"cancel": "Cancel"})
        self.assertEqual(response.status_code, 302, "User failed to correctly cancel the deletion.")
        self.assertIsNotNone(Notification.objects.filter(pk=1).first(), "The notification does not exist.")
        
    def test_post_confirm_delete(self):
        """
        Test the confirm delete functionality for the notification delete view.
        """
        # TODO: test_post_confirm_delete
        # [x]: Log in as the user that can access the view and delete the notification
        # [x]: Confirm the deletion
        # [x]: Make sure that the notification is gone
        self.client.login(username="testuser1", password="password")
        response = self.client.post(self.notification_delete_url, {"confirm": "Confirm"})
        self.assertEqual(response.status_code, 302, "User failed to correctly confirm the deletion.")
        self.assertIsNone(Notification.objects.filter(pk=1).first(), "The notification does exist.")
