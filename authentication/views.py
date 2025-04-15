""" # TODO: Update module docstring
This module defines class-based views for displaying the home page, login page, notifications, users, and user details.

### Mixins
    - LoginRequiredMixin:
        Restricts access to authenticated users. Unauthenticated users will be redirected to the login page. After logging in, they
        will be redirected back to the original destination preserved by the query parameter defined by `redirect_field_name`.
    - UserPassesTestMixin:
        Restricts access based on user-specific conditions.

### Base Classes
    - LoginView:
        Handles the login logic and renders the login page. 
    - ListView:
        Displays a list of objects.
    - DetailView:
        Shows the details of an object.
    - CreateView:
        Provides a form for creating new objects in the database.
    - UpdateView:
        Provides a form for updating existing objects in the database.
    - DeleteView:
        Confirms and processes object deletions.
"""

import json
from typing import Any
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect

from django.contrib import messages

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView

from django.urls import reverse, reverse_lazy

from django.views.decorators.http import require_http_methods
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import User, Notification
from inventory_database.mixins import SuperuserRequiredMixin

import logging
logger = logging.getLogger(__name__)



# Create your views here.
def home(request):
    """
    Renders the "home.html" template when the user accesses the home page.
    
    This method checks if the user is authenticated and retrieves the first group the user belongs to. 
    The group is then added to the context dictionary under the key "user_group". Atfer that, the 
    context is passed to the "home.html" template for rendering. A response is returned with the rendered
    template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered "home.html" template.
    """
    user_group = request.user.groups.first()
    context = {"user_group": user_group}
    return render(request, "home.html", context)


def unread_notifications_count_view(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({'unread_count': unread_count})
    return JsonResponse({'unread_count': 0})


class DatabaseLoginView(LoginView):
    """
    Class-based view to handle the login logic and render the login page.
    
    Inherits functionality from:
        - LoginView
    (See module docstring for more details on the inherited classes)
    
    Methods: 
        `form_invalid()`: Overrides the base class's `form_invalid` method and extends the behavior to display custom error messages.
    """
    
    template_name = "registration/login.html"
    
    def form_invalid(self, form):
        """
        Overrides the base class's `form_invalid` method and extends the behavior to display custom error messages.
        
        This method first extracts the username and password from the POST request. Then, it checks if the username exists
        in the database. If the username does not exist, an error message is displayed for an "invalid username". 
        If the username does exist, it checks if the password associated with the username is correct. If the 
        password is incorrect (None is returned from the `authenticate` method), an error message will be displayed 
        or an "invalid password". If the password is correct (a user object is returned by the `authenticate` 
        method), no error message will be displayed. The base class's `form_invalid` method is then called to retain
        the default behavior. 

        Args:
            form (AuthenticationForm): The form object that was submitted.
        """
        username = self.request.POST.get("username")
        password = self.request.POST.get("password")
        
        if not User.objects.filter(username=username).exists():
            messages.error(self.request, "Invalid username.")
        else:
            user = authenticate(self.request, username=username, password=password)
            if user is None:
                messages.error(self.request, "Invalid password.")

        return super().form_invalid(form)
    
    
class NotificationView(LoginRequiredMixin, ListView):
    """
    Class-based view to list all notifications for the currently logged-in user.

    Inherits functionality from:
        - LoginRequiredMixin
        - ListView
    (See module docstring for more details on the inherited classes)

    Attributes:
        `login_url (str)`: The URL to the login page (resolved using reverse_lazy).
        `redirect_field_name (str)`: The query parameter for the URL the user will be redirected to after logging in.
        `model (Notification)`: The model that this view will display.
        `template_name (str)`: The name of the template to use for rendering the view.
        `context_object_name (str)`: The name of the context variable to use for the list of notifications.
        
    Methods:
        get_queryset(): Retrieves all notifications for the currently logged-in user.
    """
    
    login_url = reverse_lazy("authentication:login")
    redirect_field_name = "next"
    model = Notification
    template_name = "notifications.html"
    context_object_name = "notifications_list"
    
    def get_queryset(self):
        """
        Retrieves all notifications for the currently logged-in user.
        
        This method retrieves the current user from the request object and filters the notifications by the user
        in reverse chronological order. The notifications are then returned as a QuerySet.

        Returns:
            QuerySet: The QuerySet of Notifications for the current user.
        """
        current_user = self.request.user
        current_user_notifications = Notification.objects.filter(user=current_user).order_by("-timestamp")
        return current_user_notifications


class NotificationUpdateView(UserPassesTestMixin, UpdateView):
    # QUESTION: Custom mixin for user notifications?
    """
    Class-based view to update a notification as read or unread.
    Users are only able to update notifications that are meant for them.

    Attributes:
        model (Notification): The model that the view will operate on.
        fields (list[str]): The fields to be displayed in the form.
        template_name (str): The template that will be used to render the page.

    Methods:
        `test_func()`: Verifies that the notification is for the current user. 
        `handle_no_permission`: Renders the 403 page with a message explaining the reason for the error.
        `get_context_data()`: Retrieves additional context data for the template.
        `get_success_url()`: Redirects back to the Notifications page upon success.
    """
    model = Notification
    fields = ["is_read"]
    template_name = "notification_update_form.html"
    
    def test_func(self):
        """
        Verifies that the notification is for the current user. 
        
        This method first retrieves the current user from the request and saves it to the `user` variable. Then, it 
        retrieves the primary key (pk) of the notification from the URL. After that, the `get_object_or_404` function is 
        used to getch the notification from the database. If no Notification object is found with the given ID or primary 
        key, an `Http404` exception is raised. If a Notification object is found, the user in the Notification's `user` 
        field is saved to the `notif_for` variable and compared with the `user` variable to see if they are the same object.

        Returns:
            bool: True if the notification is for the current user. False otherwise.
        """
        user = self.request.user
        notification_id = self.kwargs.get("pk")
        notif_for = get_object_or_404(Notification, id=notification_id).user
        return notif_for == user
    
    def handle_no_permission(self):
        """
        Renders the 403 page with a message explaining the reason for the error.

        Returns:
            HttpResponse: The HTTP response object with the rendered 403 page.
        """
        message = "This notification is not addressed to you."
        return HttpResponseForbidden(render((self.request, "403.html", {"message": message})))
    
    def get_context_data(self, **kwargs):
        """
        Retrieves additional context data for the template.
        
        This method first calls the base class's `get_context_data` method to retrieve the base context data. Then, it retrieves 
        the notification object using the primary key (pk) from the URL and adds it to the context. If the notification isn't 
        found, an `Http404` exception is raised. The context dictionary is then updated with the notification object.

        Returns:
            dict: The context data for the template.
        """
        context = super().get_context_data(**kwargs)
        notification_id = self.kwargs.get("pk")
        context["notification"] = get_object_or_404(Notification, id=notification_id)
        return context
    
    
    def get_success_url(self):
        """
        Redirects back to the Notifications page upon success.
        
        This method uses the `reverse` function to resolve the URL to the Notifications page and returns it. 

        Returns:
            str: The URL to the Notifications page.
        """
        return reverse("authentication:notifications")

    
class NotificationDeleteView(UserPassesTestMixin, DeleteView):
    """
    Handles the deletion of a notification.
    Users are only able to delete notifications that are meant for them.     
    
    Inherits functionality from:
        - UserPassesTestMixin
        - CreateView
    (See module docstring for more details on the inherited classes)

    Attributes:
        model (Notification): The model that the view will operate on.
        success_url (str): The URL to redirect to after a successful deletion (resolved using `reverse_lazy`).
        fail_url (str): The URL to redirect to if the deletion is canceled (resolved using the `get_fail_url` method).
        
    Methods:
        `test_func()`: Verifies that the notification is for the current user. 
        `handle_no_permission`: Renders the 403 page with a message explaining the reason for the error.
        `get_fail_url()`: Returns the URL to redirect to if the deletion is canceled.
        `post()`: Handles the POST request for deleting a user.
    """

    model = Notification
    success_url = reverse_lazy("authentication:notifications")
    
    def test_func(self):
        """
        Verifies that the notification is for the current user. 
        
        This method first retrieves the current user from the request and saves it to the `user` variable. Then, it 
        retrieves the primary key (pk) of the notification from the URL. After that, the `get_object_or_404` function is 
        used to getch the notification from the database. If no Notification object is found with the given ID or primary 
        key, an `Http404` exception is raised. If a Notification object is found, the user in the Notification's `user` 
        field is saved to the `notif_for` variable and compared with the `user` variable to see if they are the same object.

        Returns:
            bool: True if the notification is for the current user. False otherwise.
        """
        user = self.request.user
        notification_id = self.kwargs.get("pk")
        notif_for = get_object_or_404(Notification, id=notification_id).user
        return notif_for == user
    
    def handle_no_permission(self):
        """
        Renders the 403 page with a message explaining the reason for the error.

        Returns:
            HttpResponse: The HTTP response object with the rendered 403 page.
        """
        message = "This notification is not addressed to you."
        return HttpResponseForbidden(render((self.request, "403.html", {"message": message})))

    def get_fail_url(self):
        """
        Returns the URL to redirect to if the deletion is canceled.
        
        This method uses reverse_lazy to resolve the failure URL with the primary key (pk) of the object
        being processed and returns it.

        Returns:
            str: The URL to redirect to.
        """
        return reverse_lazy("authentication:notifications")

    fail_url = property(get_fail_url)

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request for deleting a notification.
        
        This method checks if the "Cancel" button was clicked when the form was submitted. If the button was clicked, 
        the current user is redirected back to the notifications page, which is the failure URL. If the "Confirm" button was 
        clicked (the else case), the base class's `post` method is called to process the deletion. 

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: The response after handling the POST request.
        """
        if "Cancel" in request.POST:
            return redirect(self.fail_url)
        else:
            return super(NotificationDeleteView, self).post(request, *args, **kwargs)


class UsersView(LoginRequiredMixin, ListView):
    """
    Displays a list of users.
    Users must be in the "Superuser" group to access this view.
    
    Inherits functionality from:
        - LoginRequiredMixin
        - ListView
    (See module docstring for more details on the inherited classes)

    Attributes:
        model (User): The model that the view will operate on.
        template_name (str): The template that will be used to render the page.
        context_object_name (str): The context variable name for the list of users.

    Methods:
        `get_queryset()`: Retrieves all users from the database in alphanumerical order by username, last name, and first name.
    """

    model = User
    template_name = "users.html"
    context_object_name = "users_list"

    def get_queryset(self):
        """
        Retrieves all users from the database in alphanumerical order by username, last name, and first name.

        Returns:
            QuerySet: The queryset containing all users in the database.
        """
        return User.objects.all().order_by("username", "last_name", "first_name")


class UserDetailsView(LoginRequiredMixin, DetailView):
    """
    Displays the details of a specific user.
    Users must be in the "Superuser" group to access this view.

    Inherits functionality from:
        - LoginRequiredMixin
        - DetailView
    (See module docstring for more details on the inherited classes)

    Attributes:
        model (User): The model that the view will operate on.
        template_name (str): The template that will be used to render the page.

    Methods: 
        `get_context_data()`: Retrieves additional context data for the template.
    """

    model = User
    template_name = "user_detail.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """
        Retrieves additional context data for the template.
        
        This method first calls the base class's `get_context_data` method to retrieve the base context data.
        Then, it retrieves the user object and checks if the user belongs to any groups. If the user belongs to a group,
        the group name is saved to the context dictionary under the key "user_group_name". If the user does not belong to 
        any groups, the group name is set to "No Group". The updated context data is then returned.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The context data for the template.
        """
        context = super().get_context_data(**kwargs)
        specific_user = self.get_object()
        if specific_user.groups.exists():
            context["user_detail_group_name"] = specific_user.groups.first().name
        else:
            context["user_detail_group_name"] = "No Group"
        return context


class UserCreateView(SuperuserRequiredMixin, CreateView):
    """
    Handles the creation of a new user.
    Users must be in the "Superuser" group to access this view.

    Inherits functionality from:
        - SuperuserRequiredMixin
        - CreateView
    (See module docstring for more details on the inherited classes)

    Attributes:
        model (User): The model this view operates on.
        fields (list[str]): The fields to be displayed in the form.
        template_name (str): The template that will be used to render the page.

    Methods:
        `get_context_data()`: Retrieves additional context data for the template.
        `get_success_url()`: Returns the URL to redirect to after a successful form submission.
        `form_valid()`: Handles the form submission and adds the user to the specified group.
    """

    model = User
    fields = ["username", "first_name", "last_name", "email", "password"]
    template_name = "user_create_form.html"

    def get_context_data(self, **kwargs):
        """
        Retrieves additional context data for the template.
        
        This method first calls the base class's `get_context_data` method to retrieve the base context data.
        Then, it saves the current user and all groups to the context dictionary under the keys "user" and "groups" respectively.
        The updated context data is then returned.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The updated context data for the template.
        """
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["groups"] = Group.objects.all()
        return context

    def get_success_url(self):
        """
        Returns the URL to redirect to after a successful form submission.

        Returns:
            str: The URL to redirect to.
        """
        return reverse_lazy("authentication:user_details", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        """
        Handles the form submission and adds the user to the specified group.
        
        This method hashes the password before saving the user to the database. It then retrieves the group name
        from the POST request and adds the user to the specified group. The response after form submission is returned.

        Args:
            form (ModelForm): The submitted form.

        Returns:
            HttpResponse: The response after form submission.
        """
        form.instance.password = make_password(form.cleaned_data["password"])
        response = super().form_valid(form)
        group_name = self.request.POST.get("user_group")
        group = Group.objects.get(name=group_name)
        self.object.groups.add(group)
        return response    


class UserUpdateView(SuperuserRequiredMixin, UpdateView):
    """
    Handles updates for an existing user.
    Users must be in the "Superuser" group to access this view.
    
    Inherits functionality from:
        - SuperuserRequiredMixin
        - UpdateView
    (See module docstring for more details on the inherited classes)

    Attributes:
        model (User): The model that the view will operate on.
        fields (list[str]): The fields to be displayed in the form.
        template_name (str): The tempalte that will be used to render the page.
        
    Methods:
        `get_success_url()`: Redirects back to the updated user's details upon success.
    """

    model = User
    fields = [
        "username", 
        "first_name", 
        "last_name", 
        "email", 
    ]
    template_name = "user_update_form.html"
    
    def get_success_url(self):
        """
        Redirects back to the updated user's details upon success.
        
        This method uses the `reverse` function to resolve the URL to the updated user's page and returns it. 
        The object is the user that was updated, and pk is the primary key of the user. It is passed as a keyword
        argument so the URL to the correct user's page is generated.

        Returns:
            str: The URL to the updated user's page.
        """
        return reverse("authentication:user_details", kwargs={"pk": self.object.pk})


class UserDeleteView(SuperuserRequiredMixin, DeleteView):
    """
    Handles the deletion of a user.
    Users must be in the "Superuser" group to access this view.
    
    Inherits functionality from:
        - SuperuserRequiredMixin
        - CreateView
    (See module docstring for more details on the inherited classes)

    Attributes:
        model (User): The model that the view will operate on.
        success_url (str): The URL to redirect to after a successful deletion (resolved using `reverse_lazy`).
        fail_url (str): The URL to redirect to if the deletion is canceled (resolved using the `get_fail_url` method).
        
    Methods:
        `get_fail_url()`: Returns the URL to redirect to if the deletion is canceled.
        `post()`: Handles the POST request for deleting a user.
    """

    model = User
    success_url = reverse_lazy("authentication:users")

    def get_fail_url(self):
        """
        Returns the URL to redirect to if the deletion is canceled.
        
        This method uses reverse_lazy to resolve the failure URL with the primary key (pk) of the object
        being processed and returns it.

        Returns:
            str: The URL to redirect to.
        """
        return reverse_lazy("authentication:user_details", kwargs={"pk": self.get_object().pk})

    fail_url = property(get_fail_url)

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request for deleting a user.
        
        This method checks if the "Cancel" button was clicked when the form was submitted. If the button was clicked, 
        the current user is redirected back to the user detail page, which is the failure URL. If the "Confirm" button was 
        clicked (the else case), the base class's `post` method is called to process the deletion. 

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: The response after handling the POST request.
        """
        if "Cancel" in request.POST:
            return redirect(self.fail_url)
        else:
            return super(UserDeleteView, self).post(request, *args, **kwargs)
