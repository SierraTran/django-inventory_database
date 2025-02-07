from django.test import TestCase
from django.urls import reverse
from django.test import Client

# filepath: /c:/Users/jimmyd/Documents/GitHub/django-inventory_database/authentication/tests.py
from .models import User

# Create your tests here.
class UserCreationTests(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(username="testuser", password="password")
        self.assertIsNotNone(user.id)


class PasswordHashingTests(TestCase):
    def test_password_hashing(self):
        user = User.objects.create_user(username="testuser", password="password")
        self.assertNotEqual(user.password, "password")


class UserAuthenticationTests(TestCase):
    def test_user_authentication(self):
        user = User.objects.create_user(username="testuser", password="password")
        self.assertTrue(self.client.login(username="testuser", password="password"))


class RegistrationFlowTests(TestCase):
    def test_registration_flow(self):
        response = self.client.post(
            reverse("register"),
            {"username": "testuser", "password1": "password", "password2": "password"},
        )
        self.assertEqual(response.status_code, 302)  # Assuming redirect on success


class LoginFlowTests(TestCase):
    def test_login_flow(self):
        User.objects.create_user(username="testuser", password="password")
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "password"}
        )
        self.assertEqual(response.status_code, 302)  # Assuming redirect on success


class LogoutFlowTests(TestCase):
    def test_logout_flow(self):
        """
        _summary_
        """
        User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)  # Assuming redirect on success


class RateLimitingTests(TestCase):
    def test_rate_limiting(self):
        """
        _summary_
        """
        for _ in range(10):  # Assuming rate limit is less than 10
            response = self.client.post(
                reverse("login"), {"username": "testuser", "password": "password"}
            )
        self.assertEqual(response.status_code, 429)  # Assuming 429 Too Many Requests


class SQLInjectionTests(TestCase):
    def test_sql_injection(self):
        """
        _summary_
        """
        response = self.client.post(
            reverse("login"), {"username": "' OR 1=1 --", "password": "password"}
        )
        self.assertNotEqual(response.status_code, 200)


class XSSTests(TestCase):
    def test_xss(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "<script>alert(1)</script>",
                "password1": "password",
                "password2": "password",
            },
        )
        self.assertNotContains(response, "<script>alert(1)</script>")


class EmptyFieldsTests(TestCase):
    def test_empty_fields(self):
        response = self.client.post(
            reverse("register"), {"username": "", "password1": "", "password2": ""}
        )
        self.assertFormError(response, "form", "username", "This field is required.")


class InvalidInputsTests(TestCase):
    def test_invalid_inputs(self):
        response = self.client.post(
            reverse("register"),
            {"username": "testuser", "password1": "pass", "password2": "pass"},
        )
        self.assertFormError(
            response, "form", "password1", "This password is too short."
        )


class AccountLockoutTests(TestCase):
    def test_account_lockout(self):
        """
        """
        user = User.objects.create_user(username="testuser", password="password")
        for _ in range(5):  # Assuming lockout after 5 attempts
            self.client.post(
                reverse("login"), {"username": "testuser", "password": "wrongpassword"}
            )
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "password"}
        )
        self.assertEqual(response.status_code, 403)  # Assuming 403 Forbidden on lockout


class LoadTestingTests(TestCase):
    def test_load_testing(self):
        for _ in range(1000):  # Simulate 1000 requests
            response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)


# Regression Tests
# class RegressionTests(TestCase):
#     # Previous Issues