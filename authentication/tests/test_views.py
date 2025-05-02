""" 
This module contains tests for the authentication app's views.
"""

import datetime
from django.test import Client, TestCase, tag
from django.urls import reverse
from django.utils import timezone

from django.contrib.auth.models import User, Group
from freezegun import freeze_time
from authentication.models import Notification


class HomeViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.user.groups.add(cls.superuser_group)
        cls.home_url = reverse("authentication:home")
        cls.client = Client()

    def test_home_view_unauthenticated(self):
        """
        Test that the home view is rendered correctly when not logged in
        """
        response = self.client.get(self.home_url)

        self.assertTemplateUsed(response, "home.html")
        self.assertFalse(
            response.wsgi_request.user.is_authenticated,
            "The user is unexpectedly authenticated.",
        )
        self.assertContains(
            response,
            '<p>Please <a href="/inventory_database/login/">log in</a> to see the database.</p>',
        )

    def test_home_view_authenticated(self):
        """
        Test that the home view is rendered correctly when logged in
        """
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.home_url)

        self.assertTemplateUsed(response, "home.html")
        self.assertTrue(
            response.wsgi_request.user.is_authenticated,
            "The user is not authenticated.",
        )
        self.assertNotContains(
            response,
            '<p>Please <a href="/inventory_database/login/">log in</a> to see the database.</p>',
        )


class DatabaseLoginViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(Group.objects.get(name="Superuser"))
        cls.login_url = reverse("authentication:login")
        cls.client = Client()

    def test_login_invalid_username(self):
        """
        An error message displays for an invalid username
        """
        response = self.client.post(
            self.login_url, {"username": "invalid", "password": "password"}
        )
        self.assertEqual(
            response.status_code, 200, "The user was unexpectedly redirected."
        )
        self.assertContains(response, "Invalid username.")
        self.assertFalse(
            response.wsgi_request.user.is_authenticated,
            "The user is unexpectedly authenticated.",
        )

    def test_login_invalid_password(self):
        """
        An error message displays for an invalid password
        """
        response = self.client.post(
            self.login_url, {"username": "testuser", "password": "invalid"}
        )
        self.assertEqual(
            response.status_code, 200, "The user was unexpectedly redirected."
        )
        self.assertContains(response, "Invalid password.")
        self.assertFalse(
            response.wsgi_request.user.is_authenticated,
            "The user is unexpectedly authenticated.",
        )

    def test_login_success(self):
        """
        Successfully login and redirect to the home page
        """
        response = self.client.post(
            self.login_url, {"username": "testuser", "password": "password"}
        )
        self.assertEqual(response.status_code, 302, "The user failed to log in.")
        self.assertTrue(
            response.wsgi_request.user.is_authenticated,
            "The user is not authenticated.",
        )


###################################################################################################
# Tests for the Views for the Notification Model ##################################################
###################################################################################################
class NotificationViewTests(TestCase):
    # TEST: NotificationViewTests
    # NOTE: Local date and time is set to January 1, 2025 at 12:00 for testing purposes
    aware_datetime = timezone.make_aware(datetime.datetime(2025, 1, 1, 12, 0, 0))

    @classmethod
    @freeze_time(aware_datetime)
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up for NotificationViewTests
        # [x]: Set date and time for testing
        # [x]: Create a user for any group
        # [ ]: Bulk create notifications for the user as well as ones not for the user
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.user1 = User.objects.create_user(username="testuser1", password="password")
        cls.user1.groups.add(cls.superuser_group)

        cls.technician_group = Group.objects.get(name="Technician")
        cls.user2 = User.objects.create_user(username="testuser2", password="password")
        cls.user2.groups.add(cls.technician_group)

        notifications = [
            Notification(
                subject="Low Stock Alert",
                message="An item in the database is below the minimum quantity.",
                user=cls.user1,
            ),
            Notification(
                subject="New Item Request",
                message="A new item request has been created.",
                user=cls.user1,
            ),
            Notification(
                subject="Welcome!",
                message="Welcome to the Inventory Database!",
                user=cls.user2,
            ),
        ]
        Notification.objects.bulk_create(notifications)
        cls.notifications_url = reverse("authentication:notifications")

        cls.client = Client()

    @tag("critical")
    def test_notification_view_get(self):
        """
        User has access to their notification page, which only show notifications addressed to them.
        """
        login = self.client.login(username="testuser1", password="password")
        self.assertTrue(login, "Login failed.")

        response = self.client.get(self.notifications_url)
        self.assertEqual(
            response.status_code, 200, "Failed to access the notifications page."
        )
        self.assertTemplateUsed(
            response,
            "notifications.html",
            "The correct template for the view is not used.",
        )

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
        self.assertEqual(
            response.status_code, 200, "Failed to access the notifications page."
        )
        self.assertTemplateUsed(
            response,
            "notifications.html",
            "The correct template for the view is not used.",
        )

    def test_notification_all_unread_notifs(self):
        # TODO: test_notification_all_unread_notifs
        """
        Test that all (unread) notifications are shown in bold, and the notification badge is shown
        with the number of unread notifications.
        """
        # [x]: Log in and access the notification page
        # [ ]: Check for notifications (all should be bold)
        # [x]: Make sure notification badge shows with correct number of unread notifications
        login = self.client.login(username="testuser1", password="password")
        self.assertTrue(login, "Login failed.")

        response = self.client.get(self.notifications_url)
        self.assertEqual(
            response.status_code, 200, "Failed to access the notifications page."
        )
        self.assertTemplateUsed(
            response,
            "notifications.html",
            "The correct template for the view is not used.",
        )
        self.assertContains(response, '<span id="notification-badge" class="badge">2</span>')

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
        self.assertEqual(
            response.status_code, 200, "Failed to access the notifications page."
        )
        self.assertTemplateUsed(
            response,
            "notifications.html",
            "The correct template for the view is not used.",
        )

    def test_notification_read_and_unread_notifs(self):
        """
        Unread notifications are shown in bold while read notifications are not in bold. 
        The notification badge will only count unread notifications.
        """
        # TODO: test_notification_read_and_unread_notifs
        # [ ]: Mark some notifications as read
        # [x]: Log in and access the notification page
        # [ ]: Check for unread notifications (shown in bold) and read notifications (now shown in bold)
        # [ ]: Make sure notification badge shows with correct number of unread notifications
        login = self.client.login(username="testuser1", password="password")
        self.assertTrue(login, "Login failed.")

        response = self.client.get(self.notifications_url)
        self.assertEqual(
            response.status_code, 200, "Failed to access the notifications page."
        )
        self.assertTemplateUsed(
            response,
            "notifications.html",
            "The correct template for the view is not used.",
        )


class NotificationUpdateViewTests(TestCase):
    # NOTE: Date and time is set to January 1, 2025 at 12:00 for testing purposes
    aware_datetime = timezone.make_aware(datetime.datetime(2025, 1, 1, 12, 0, 0))

    @classmethod
    @freeze_time(aware_datetime)
    def setUpTestData(cls):
        """
        Setup
        """
        cls.user_with_access = User.objects.create_user(
            username="testuser1", password="password"
        )
        cls.user_with_no_access = User.objects.create_user(
            username="testuser2", password="password"
        )

        Notification.objects.create(
            # is_read automatically set to false
            subject="Welcome!",
            message="Welcome to the Inventory Database.",
            # timestamp automatically set
            user=cls.user_with_access,
        )
        cls.notification = Notification.objects.filter(pk=1).first()
        cls.notification_update_url = reverse(
            "authentication:notification_update_form",
            kwargs={"pk": cls.notification.pk},
        )

        cls.client = Client()

    @tag("critical")
    def test_notification_update_view_access_control(self):
        """
        Access control for the notification update view.
        """
        self.client.login(username="testuser1", password="password")
        response = self.client.get(self.notification_update_url)
        self.assertEqual(
            response.status_code,
            200,
            "The user failed to access the update view for their notification.",
        )
        self.client.logout()

        self.client.login(username="testuser2", password="password")
        response = self.client.get(self.notification_update_url)
        self.assertEqual(
            response.status_code,
            403,
            "User unexpectedly gained access to update view for notification that isn't for them.",
        )
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
        cls.user_with_access = User.objects.create_user(
            username="testuser1", password="password"
        )
        cls.user_with_no_access = User.objects.create_user(
            username="testuser2", password="password"
        )

        Notification.objects.create(
            # is_read automatically set to false
            subject="Welcome!",
            message="Welcome to the Inventory Database.",
            # timestamp automatically set
            user=cls.user_with_access,
        )
        cls.notification = Notification.objects.filter(pk=1).first()
        cls.notification_delete_url = reverse(
            "authentication:notification_confirm_delete",
            kwargs={"pk": cls.notification.pk},
        )

        cls.client = Client()

    def test_notification_delete_view_access_control(self):
        """
        Test the access control for the notification delete view.
        """
        self.client.login(username="testuser1", password="password")
        response = self.client.get(self.notification_delete_url)
        self.assertEqual(
            response.status_code,
            200,
            "The user failed to access the update view for their notification.",
        )
        self.client.logout()

        self.client.login(username="testuser2", password="password")
        response = self.client.get(self.notification_delete_url)
        self.assertEqual(
            response.status_code,
            403,
            "User gained access to update view for a notification that isn't for them.",
        )
        self.client.logout()

    def test_post_cancel_delete(self):
        """
        Test the cancel delete functionality for the notification delete view.
        """
        self.client.login(username="testuser1", password="password")
        response = self.client.post(self.notification_delete_url, {"cancel": "Cancel"})
        self.assertEqual(
            response.status_code, 302, "User failed to correctly cancel the deletion."
        )
        self.assertIsNotNone(
            Notification.objects.filter(pk=1).first(),
            "The notification does not exist.",
        )

    def test_post_confirm_delete(self):
        """
        Test the confirm delete functionality for the notification delete view.
        """
        self.client.login(username="testuser1", password="password")
        response = self.client.post(
            self.notification_delete_url, {"confirm": "Confirm"}
        )
        self.assertEqual(
            response.status_code, 302, "User failed to correctly confirm the deletion."
        )
        self.assertIsNone(
            Notification.objects.filter(pk=1).first(), "The notification does exist."
        )
