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
    """
    Tests for the home view
    """
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


class UnreadNotificationsCountViewTests(TestCase):
    """
    Tests for the unread notifications count view
    """

    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.user.groups.add(cls.superuser_group)

        # Create some notifications for the user
        Notification.objects.create(
            subject="Test Notification 1",
            message="This is a test notification.",
            user=cls.user,
        )
        Notification.objects.create(
            subject="Test Notification 2",
            message="This is another test notification.",
            user=cls.user,
            is_read=True,
        )

        cls.unread_notifications_url = reverse("authentication:unread_notifications_count")

        cls.client = Client()

    def test_unread_notifications_count_unauthenticated(self):
        """
        Test that the unread notifications count is 0 when not logged in
        """
        response = self.client.get(self.unread_notifications_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"unread_count": 0})

    def test_unread_notifications_count_authenticated(self):
        """
        Test that the unread notifications count is correct when logged in
        """
        self.client.login(username="testuser", password="password")   
        response = self.client.get(self.unread_notifications_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"unread_count": 1})


class DatabaseLoginViewTests(TestCase):
    """
    Tests for the login view
    """
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
    """
    Tests for NotificaionView
    """
    # NOTE: Local date and time is set to January 1, 2025 at 12:00 for testing purposes
    aware_datetime = timezone.make_aware(datetime.datetime(2025, 1, 1, 12, 0, 0))

    @classmethod
    @freeze_time(aware_datetime)
    def setUpTestData(cls):
        """
        Setup
        """
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
        """
        No notifications or notification badge will be shown.
        """
        # TODO: Make sure the notification badge doesn't show; need selenium for this
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
        self.assertContains(response, "<p>There are no notifications.</p>")

    def test_notification_all_unread_notifs(self):
        """
        Test that all (unread) notifications are shown in bold, and the notification badge is shown
        with the number of unread notifications.
        """
        # TODO: Check for notifications (all should be bold); need selenium for this
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
        """
        All notifications are not shown in bold, and the notification badge won't be shown.
        """
        # Mark all notifications as read
        Notification.objects.filter(user=self.user1).update(is_read=True)
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

        # Check that notifications are not bold (assuming bold is <strong>)
        for notif in Notification.objects.filter(user=self.user1):
            self.assertNotContains(response, f"<strong>{notif.subject}</strong>")

    def test_notification_read_and_unread_notifs(self):
        """
        Unread notifications are shown in bold while read notifications are not in bold. 
        The notification badge will only count unread notifications.
        """
        # Mark one notification as read, one as unread
        notifs = Notification.objects.filter(user=self.user1)
        unread_notif = notifs.first()
        read_notif = notifs.last()
        read_notif.is_read = True
        read_notif.save()
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
        # Badge should show 1 unread
        self.assertContains(response, '<span id="notification-badge" class="badge">1</span>')
        # TODO: Unread notification should be bold; need selenium for this
        # self.assertContains(response, f"<strong>{unread_notif.subject}</strong>")
        # TODO: Read notification should not be bold; need selenium for this
        # self.assertNotContains(response, f"<strong>{read_notif.subject}</strong>")


class NotificationUpdateViewTests(TestCase):
    """
    Tests for NotificationUpdateView
    """
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
        self.client.login(username="testuser1", password="password")
        response = self.client.get(self.notification_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("notification", response.context)
        self.assertEqual(response.context["notification"], self.notification)

    def test_update_notification(self):
        """
        Test that the notification can be updated correctly.
        """
        self.client.login(username="testuser1", password="password")
        # Mark as read
        response = self.client.post(
            self.notification_update_url,
            {"is_read": True, "subject": self.notification.subject, "message": self.notification.message},
        )
        self.assertEqual(response.status_code, 302)
        notif = Notification.objects.get(pk=self.notification.pk)
        self.assertTrue(notif.is_read)


class NotificationDeleteViewTests(TestCase):
    """
    Tests for NotificationDeleteView
    """
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


###################################################################################################
# Tests for the Views for the User Model ##########################################################
###################################################################################################
class UsersViewTests(TestCase):
    """
    Tests for UserView
    """
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.user1 = User.objects.create_user(username="testuser1", password="password")
        cls.user1.groups.add(cls.superuser_group)

        cls.technician_group = Group.objects.get(name="Technician")
        cls.user2 = User.objects.create_user(username="testuser2", password="password")
        cls.user2.groups.add(cls.technician_group)

        cls.users_url = reverse("authentication:users")
        cls.client = Client()

    def test_get_queryset(self):
        """
        Test the queryset for the user list view.
        """
        # Log in as superuser and check that all users are in the queryset
        self.client.login(username="testuser1", password="password")
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, 200)
        # Both users should be in the context
        users = response.context["users_list"]
        usernames = [user.username for user in users]
        self.assertIn("testuser1", usernames)
        self.assertIn("testuser2", usernames)
        self.client.logout()

        # Log in as technician and check that all users are still visible
        self.client.login(username="testuser2", password="password")
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, 200)
        users = response.context["users_list"]
        usernames = [user.username for user in users]
        self.assertIn("testuser1", usernames)
        self.assertIn("testuser2", usernames)
        self.client.logout()


class UserDetailsViewTests(TestCase):
    """
    Tests for UserDetailsView
    """
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.user1 = User.objects.create_user(username="testuser1", password="password")
        cls.user1.groups.add(cls.superuser_group)

        cls.technician_group = Group.objects.get(name="Technician")
        cls.user2 = User.objects.create_user(username="testuser2", password="password")
        cls.user2.groups.add(cls.technician_group)
        
        cls.user3 = User.objects.create_user(username="testuser3", password="password")
        # User 3 is not assigned to any group

        cls.users_url = reverse("authentication:users")
        cls.client = Client()

    def test_get_context_data(self):
        """
        Test the context data for the user details view.
        """
        # Log in as superuser and access user details for technician
        self.client.login(username="testuser1", password="password")
        user_detail_url = reverse("authentication:user_details", kwargs={"pk": self.user2.pk})
        response = self.client.get(user_detail_url)
        self.assertEqual(response.status_code, 200)
        # Check that the context contains the correct user
        self.assertEqual(response.context["user"].username, "testuser2")
        # Check for group info in context if provided
        if "groups" in response.context:
            group_names = [g.name for g in response.context["groups"]]
            self.assertIn("Technician", group_names)
        # Access user details for User 3
        user_detail_url = reverse("authentication:user_details", kwargs={"pk": self.user3.pk})
        response = self.client.get(user_detail_url)
        self.assertEqual(response.status_code, 200)
        # Check that the context contains the correct user
        self.assertEqual(response.context["user"].username, "testuser3")
        # Check for group info in context (no groups assigned)
        if "groups" in response.context:
            group_names = [g.name for g in response.context["groups"]]
            self.assertEqual(group_names, [], "User 3 should not have any groups assigned.")
        self.client.logout()

        # Log in as technician and access own details
        self.client.login(username="testuser2", password="password")
        user_detail_url = reverse("authentication:user_details", kwargs={"pk": self.user2.pk})
        response = self.client.get(user_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["user"].username, "testuser2")
        self.client.logout()


class UserCreateViewTests(TestCase):
    """
    Tests for UserCreateView
    """
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.user1 = User.objects.create_user(username="testuser1", password="password")
        cls.user1.groups.add(cls.superuser_group)

        cls.technician_group = Group.objects.get(name="Technician")
        cls.user2 = User.objects.create_user(username="testuser2", password="password")
        cls.user2.groups.add(cls.technician_group)

        cls.users_url = reverse("authentication:users")
        cls.client = Client()
        cls.user_create_url = reverse("authentication:user_create_form")

    def test_user_create_view_access_control(self):
        """
        Test the access control for the user create view.
        """
        # Log in as superuser and access user create view
        self.client.login(username="testuser1", password="password")
        response = self.client.get(self.user_create_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        # Log in as technician and try to access user create view
        self.client.login(username="testuser2", password="password")
        response = self.client.get(self.user_create_url)
        self.assertEqual(response.status_code, 403)

    def test_post_create_user(self):
        """
        Test the create user functionality for the user create view.
        """
        # Log in as superuser and access user create view
        self.client.login(username="testuser1", password="password")
        response = self.client.post(
            self.user_create_url,
            {
                "username": "newuser",
                "password": "newpassword",
                "user_group": self.technician_group.name,
            },
        )
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.filter(username="newuser").first()
        self.assertIsNotNone(new_user, "The new user does not exist.")


class UserUpdateViewTests(TestCase):
    """
    Tests for UserUpdateView
    """

    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.user1 = User.objects.create_user(username="testuser1", password="password")
        cls.user1.groups.add(cls.superuser_group)

        cls.technician_group = Group.objects.get(name="Technician")
        cls.user2 = User.objects.create_user(username="testuser2", password="password")
        cls.user2.groups.add(cls.technician_group)

        cls.users_url = reverse("authentication:users")
        cls.client = Client()
        cls.user_update_url = reverse(
            "authentication:user_update_form", kwargs={"pk": cls.user2.pk}
        )

    def test_user_update_view_access_control(self):
        """
        Test that only superusers can access the user update view.
        """
        # Log in as superuser and access user update view
        self.client.login(username="testuser1", password="password")
        response = self.client.get(self.user_update_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        # Log in as technician and try to access user update view
        self.client.login(username="testuser2", password="password")
        response = self.client.get(self.user_update_url)
        self.assertEqual(response.status_code, 403)
        
    def test_update_user(self):
        """
        Test the update user functionality for the user update view.
        """
        # Log in as superuser and access user update view
        self.client.login(username="testuser1", password="password")
        response = self.client.post(
            self.user_update_url,
            {
                "username": "updateduser",
                "password": "updatedpassword",
                "user_group": self.technician_group.name,
            },
        )
        self.assertEqual(response.status_code, 302)
        updated_user = User.objects.filter(username="updateduser").first()
        self.assertIsNotNone(updated_user, "The updated user does not exist.")


class UserDeleteViewTests(TestCase):
    """
    Tests for UserDeleteView
    """
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.user1 = User.objects.create_user(username="testuser1", password="password")
        cls.user1.groups.add(cls.superuser_group)

        cls.technician_group = Group.objects.get(name="Technician")
        cls.user2 = User.objects.create_user(username="testuser2", password="password")
        cls.user2.groups.add(cls.technician_group)

        cls.users_url = reverse("authentication:users")
        cls.user_delete_url = reverse(
            "authentication:user_confirm_delete", kwargs={"pk": cls.user2.pk}
        )
        cls.client = Client()

    @tag("critical")
    def test_user_delete_view_access_control(self):
        """
        Test the access control for the user delete view.
        """
        # Log in as superuser and access user delete view
        self.client.login(username="testuser1", password="password")
        response = self.client.get(self.user_delete_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        # Log in as technician and try to access user delete view
        self.client.login(username="testuser2", password="password")
        response = self.client.get(self.user_delete_url)
        self.assertEqual(response.status_code, 403)

    def test_post_cancel_delete(self):
        """
        Test the cancel delete functionality for the user delete view.
        """
        # Log in as superuser and access user delete view
        self.client.login(username="testuser1", password="password")
        self.assertIsNotNone(
            User.objects.filter(pk=self.user2.pk).first(),
            "Before cancellation: The user does not exist.",
        )
        response = self.client.post(self.user_delete_url, {"cancel": "Cancel"})
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(
            User.objects.filter(pk=self.user2.pk).first(),
            "After cancellation: The user does not exist.",
        )

    def test_post_confirm_delete(self):
        """
        Test the confirm delete functionality for the user delete view.
        """
        # Log in as superuser and access user delete view
        self.client.login(username="testuser1", password="password")
        self.assertIsNotNone(
            User.objects.filter(pk=self.user2.pk).first(),
            "Before confirmation: The user does not exist.",
        )
        response = self.client.post(self.user_delete_url, {"confirm": "Confirm"})
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(
            User.objects.filter(pk=self.user2.pk).first(),
            "After confirmation: The user does exist.",
        )
