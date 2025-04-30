"""
    This module holds custon mixins for the project, specifically for allowing users in certain
    groups to access certain views. The mixins are used in the views.py file of both apps.
    
    ### Mixins:
        - UserPassesTestMixin: 
            This mixin is used for checking if a user passes a certain test. It is used as a base
            class for the other mixins.
        
            See more info in the Django documentation:
            https://docs.djangoproject.com/en/3.2/topics/auth/default/#django.contrib.auth.mixins.UserPassesTest)
"""

from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render

class SuperuserRequiredMixin(UserPassesTestMixin):
    """
    A mixin that allows only users in the "Superuser" group to access the view.

    Methods:
        `test_func()`: Verifies if the user is in the "Superuser" group.
        `handle_no_permission()`: Renders the 403 page with a message explaining the reason for the
            error.
    """
    def test_func(self) -> bool:
        """
        Verifies if the user is in the "Superuser" group.
        
        This method checks the first group the current user belongs to. If the group exists and its
        name is "Superuser", it returns True; otherwise, it returns False.

        Returns:
            bool: True if the user is in the "Superuser" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name == "Superuser"

    def handle_no_permission(self):
        """
        Renders the 403 page with a message explaining the reason for the error.

        Returns:
            HttpResponse: The HTTP response object with the rendered 403 page.
        """
        message = "You need to be a Superuser to access this view."
        return HttpResponseForbidden(render(self.request, "403.html", {"message": message}))


class SuperuserOrTechnicianRequiredMixin(UserPassesTestMixin):
    """
    A mixin that allows only users in the "Superuser" or "Technician" group to access the view.

    Methods:
        `test_func()`: Verifies if the user is in the "Superuser" or "Technician" group.
        `handle_no_permission()`: Renders the 403 page with a message explaining the reason for the
            error.
    """
    def test_func(self) -> bool:
        """
        Verifies if the user is in the "Superuser" or "Technician" group.
        
        This method checks the first group the current user belongs to. If the group exists and its
        name is "Superuser" or "Technician", it returns True; otherwise, it returns False.

        Returns:
            bool: True if the user is in the "Superuser" or "Technician" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name in ["Superuser", "Technician"]

    def handle_no_permission(self):
        """
        Renders the 403 page with a message explaining the reason for the error.

        Returns:
            HttpResponse: The HTTP response object with the rendered 403 page.
        """
        message = "You need to be a Superuser or Technician to access this view."
        return HttpResponseForbidden(render(self.request, "403.html", {"message": message}))


class TechnicianRequiredMixin(UserPassesTestMixin):
    """
    A mixin that allows only users in the "Technician" group to access the view.

    Methods:
        `test_func()`: Verifies if the user is in the "Technician" group.
        `handle_no_permission()`: Renders the 403 page with a message explaining the reason for the
            error.
    """
    def test_func(self) -> bool:
        """
        Verifies if the user is in the "Technician" group.
        
        This method checks the first group the current user belongs to. If the group exists and its
        name is "Technician", it returns True; otherwise, it returns False.

        Returns:
            bool: True if the user is in the "Technician" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name == "Technician"

    def handle_no_permission(self):
        """
        Renders the 403 page with a message explaining the reason for the error.

        Returns:
            HttpResponse: The HTTP response object with the rendered 403 page.
        """
        message = "You need to be a Technician to access this view."
        return HttpResponseForbidden(render(self.request, "403.html", {"message": message}))


class InternRequiredMixin(UserPassesTestMixin):
    """
    A mixin that allows only users in the "Intern" group to access the view.

    Methods:
        `test_func()`: Verifies if the user is in the "Intern" group.
        `handle_no_permission()`: Renders the 403 page with a message explaining the reason for the
            error.
    """
    def test_func(self) -> bool:
        """
        Verifies if the user is in the "Intern" group.
        
        This method checks the first group the current user belongs to. If the group exists and its
        name is "Intern", it returns True; otherwise, it returns False.

        Returns:
            bool: True if the user is in the "Intern" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name == "Intern"

    def handle_no_permission(self):
        """
        Renders the 403 page with a message explaining the reason for the error.

        Returns:
            HttpResponse: The HTTP response object with the rendered 403 page.
        """
        message = "You need to be a Intern to access this view."
        return HttpResponseForbidden(render(self.request, "403.html", {"message": message}))
