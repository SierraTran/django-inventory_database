from django.test import Client, TestCase, tag
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time

from django.contrib.auth.models import User, Group
from authentication.models import Notification

import datetime

# Create your tests here.


class NotificationModelTests(TestCase):
    # NOTE: Local date and time is set to January 1, 2025 at 12:00 for testing purposes
    aware_datetime = timezone.make_aware(datetime.datetime(2025, 1, 1, 12, 0, 0))

    @classmethod
    @freeze_time(aware_datetime)
    def setUpTestData(cls):
        """
        Setup
        """
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(Group.objects.get_or_create(name="Superuser")[0])

        notifications = [
            Notification(
                subject="Welcome!",
                message="Welcome to the Inventory Database!",
                user=cls.user,
            ),
            Notification(
                subject="Reminder",
                message="Don't forget to update your profile.",
                user=cls.user,
            ),
        ]
        Notification.objects.bulk_create(notifications)

    def test_notification_user_relationship(self):
        """
        Test that the notification is associated with the right user.
        """
        notification = Notification.objects.get(pk=1)
        self.assertEqual(
            notification.user, self.user, "The notification user does not match."
        )

    def test_notification_creation(self):
        """
        Test that notifications are created correctly.
        """
        notifications = Notification.objects.filter(user=self.user)
        self.assertEqual(
            notifications.count(), 2, "The number of notifications does not match."
        )

    def test_notification_is_read_default(self):
        """
        Test that the default value of is_read is False.
        """
        notification = Notification.objects.get(pk=1)
        self.assertFalse(
            notification.is_read, "The default value of is_read should be False."
        )

    def test_notification_timestamp(self):
        """
        Test that the timestamp is set correctly.
        """
        # NOTE: The timestamp is stored in UTC in the database.
        notification = Notification.objects.get(pk=1)
        self.assertEqual(
            notification.timestamp.strftime("%Y-%m-%d %I:%M:%S %p"),
            "2025-01-01 05:00:00 PM",
            "The timestamp does not match the expected value.",
        )

    def test___str__(self):
        """
        String representation is printed in expected format.
        """
        notification = Notification.objects.get(pk=1)

        self.assertEqual(
            str(notification),
            '2025-01-01 12:00:00 PM | For testuser: "Welcome!"',
            "The string representation does not match.",
        )
