"""
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

from typing import Any
from django import forms
from django.shortcuts import render, redirect

from django.contrib import messages

from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView

from django.urls import reverse, reverse_lazy

from django.views.generic import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import User, Notification


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


class DatabaseLoginView(LoginView):
    """
    Class-based view to handle the login logic and render the login page.
    
    Inherits functionality from:
        - LoginView
    (See module docstring for more details on the inherited classes)
    
    Methods: 
        `form_invalid()`: Overrides the base class's `form_invalid` method and extends the behavior to display custom error messages.
    """
    
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
            form (AuthenticationForm): _description_
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
    
    
class NotificationsView(LoginRequiredMixin, ListView):
    # TODO: Update docstring to explain login_url and redirect_field_name
    """
    Class-based view to list all notifications for the currently logged-in user.

    Inherits functionality from:
        - LoginRequiredMixin
        - ListView
    (See module docstring for more details on the inherited classes)

    Attributes:
        login_url (str): 
        redirect_field_name (str):  
        model (Notification): The model that this view will display.
        template_name (str): The name of the template to use for rendering the view.
        context_object_name (str): The name of the context variable to use for the list of notifications.
        
    Methods:
        get_queryset(): Retrieves all notifications for the currently logged-in user.
    """
    login_url = reverse_lazy("login")
    redirect_field_name = "next"
    model = Notification
    template_name = "notifications.html"
    context_object_name = "notifications_list"
    
    def get_queryset(self):
        # TODO: Update docstring to explain what the method does in detail
        """
        Retrieves all notifications for the currently logged-in user.

        Returns:
            QuerySet: The QuerySet of Notifications for the current user.
        """
        current_user = self.request.user
        current_user_notifications = Notification.objects.filter(user=current_user).order_by("-timestamp")
        return current_user_notifications
    

class UsersView(UserPassesTestMixin, ListView):
    # TODO: Update docstring to explain methods
    """
    Displays a list of users.

    Attributes:
        model (User): The model that the view will operate on.
        template_name (str): The template that will be used to render the page.
        context_object_name (str): The context variable name for the list of users.

    Methods:
        `test_func()`: Verifies if the user is in the "Superuser" group.
        `handle_no_permission()`: 
    """

    model = User
    template_name = "users.html"
    context_object_name = "users_list"

    def test_func(self) -> bool:
        """
        Verifies if the user is in the "Superuser" group.
        
        This method checks the first group the current user belongs to. If the group exists and its name is 
        'Superuser', it returns True; otherwise, it returns False.

        Returns:
            bool: True if the user is in the "Superuser" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name == "Superuser"
    
    def handle_no_permission(self):
        """
        Renders the 403 page with a message explaining the error.

        Returns:
            HttpResponse: The HTTP response object with the rendered 403 page.
        """
        message = "You need to be a Superuser to access this view."
        return render(self.request, "403.html", {"message": message})

    def get_queryset(self):
        """
        Retrieves all users from the database.

        Returns:
            QuerySet: The queryset containing all users in the database.
        """
        return User.objects.all().order_by("username", "last_name", "first_name")


class UserDetailsView(UserPassesTestMixin, DetailView):
    # TODO: Update docstring
    """
    Displays the details of a specific user.

    Inherits functionality from:
        - UserPassesTestMixin
        - DetailView
    (See module docstring for more details on the inherited classes)

    Attributes:
        model (User): The model that the view will operate on.
        template_name (str): The template that will be used to render the page.

    Methods: 
        `test_func()`: Verifies is the user is in the "Superuser" group.
        `handle_no_permission()`: Renders the 403 page with a message explaining the error.
        `get_context_data()`: 
    """

    model = User
    template_name = "user_detail.html"

    def test_func(self) -> bool:
        """
        Verifies if the user is in the "Superuser" group.
        
        This method checks the first group the current user belongs to. If the group exists and its name is 
        'Superuser', it returns True; otherwise, it returns False.

        Returns:
            bool: True if the user is in the "Superuser" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name == "Superuser"
    
    def handle_no_permission(self):
        """
        Renders the 403 page with a message explaining the error.

        Returns:
            HttpResponse: The HTTP response object with the rendered 403 page.
        """
        message = "You need to be a Superuser to access this view."
        return render(self.request, "403.html", {"message": message})

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        # TODO: Update docstring
        # TODO: Update method. Only superusers can access the view, so there may be no need to handle the case where there's no group.
        """
        Retrieves additional context data for the template.

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


class CreateUserView(UserPassesTestMixin, CreateView):
    """
    Handles the creation of a new user.
    Users must be in the "Superuser" group to access this view.

    Inherits functionality from:
        - UserPassesTestMixin
        - CreateView
    (See module docstring for more details on the inherited classes)

    Attributes:
        model (User): The model this view operates on.
        fields (list[str]): The fields to be displayed in the form.
        template_name (str): The template that will be used to render the page.

    Methods:
        `get_context_data()`: Retrieves additional context data for the template.
        `get_success_url()`: Returns the URL to redirect to after a successful form submission.
        `test_func()`: Verifies if the user is in the "Superuser" group.
        `handle_no_permission()`: Renders the 403 page with a message explaining the error.
        `form_valid()`: Handles the form submission and adds the user to the specified group.
    """

    model = User
    fields = ["username", "first_name", "last_name", "email", "password"]
    template_name = "user_create_form.html"

    def get_context_data(self, **kwargs):
        # TODO: Update docstring
        """
        Retrieves additional context data for the template.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The context data for the template.
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

    def test_func(self) -> bool:
        """
        Verifies if the user is in the "Superuser" group.
        
        This method checks the first group the current user belongs to. If the group exists and its name is 
        'Superuser', it returns True; otherwise, it returns False.

        Returns:
            bool: True if the user is in the "Superuser" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name == "Superuser"
    
    def handle_no_permission(self):
        """
        Renders the 403 page with a message explaining the error.

        Returns:
            HttpResponse: The HTTP response object with the rendered 403 page.
        """
        message = "You need to be a Superuser to access this view."
        return render(self.request, "403.html", {"message": message})

    def form_valid(self, form):
        # TODO: Update docstring
        """
        Handles the form submission and adds the user to the specified group.

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


class UpdateUserView(UserPassesTestMixin, UpdateView):
    # TODO: Update docstring
    """
    Handles updates for an existing user.

    Attributes:
        model (User): The model that the view will operate on.
        fields (list[str]): The fields to be displayed in the form.
        template_name (str): The tempalte that will be used to render the page.
    """

    model = User
    fields = [
        "username", 
        "first_name", 
        "last_name", 
        "email", 
    ]
    template_name = "user_update_form.html"

    def test_func(self) -> bool:
        """
        Verifies if the user is in the "Superuser" group.
        
        This method checks the first group the current user belongs to. If the group exists and its name is 
        'Superuser', it returns True; otherwise, it returns False.

        Returns:
            bool: True if the user is in the "Superuser" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name == "Superuser"
    
    def handle_no_permission(self):
        """
        Renders the 403 page with a message explaining the error.

        Returns:
            HttpResponse: The HTTP response object with the rendered 403 page.
        """
        message = "You need to be a Superuser to access this view."
        return render(self.request, "403.html", {"message": message})

    def get_context_data(self, **kwargs):
        # TODO: Docstring
        context = super().get_context_data(**kwargs)        
        return context
    
    def get_success_url(self):
        # TODO: Update docstring
        """
        Redirects back to the updated user's details upon success.

        Returns:
            str: The URL to the updated user's page.
        """
        return reverse("authentication:user_details", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        return super().form_valid(form)


class DeleteUserView(UserPassesTestMixin, DeleteView):
    # TODO: Update docstring
    """
    Handles the deletion of a user.
    
    Inherits functionality from:
        - UserPassesTestMixin
        - CreateView
    (See module docstring for more details on the inherited classes)

    Attributes:
        model (User): The model that the view will operate on.
        success_url (str): The URL to redirect to after a successful deletion (resolved using `reverse_lazy`).
        fail_url (str): The URL to redirect to if the deletion is canceled (resolved using the `get_fail_url` method).
        
    Methods:
        `get_fail_url()`: Returns the URL to redirect to if the deletion is canceled.
        `test_func()`: Verifies if the user is in the "Superuser" group.
        `handle_no_permission()`: Renders the 403 page with a message explaining the error.
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

    def test_func(self) -> bool:
        """
        Verifies if the user is in the "Superuser" group.
        
        This method checks the first group the current user belongs to. If the group exists and its name is 
        'Superuser', it returns True; otherwise, it returns False.

        Returns:
            bool: True if the user is in the "Superuser" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name == "Superuser"
    
    def handle_no_permission(self):
        """
        Renders the 403 page with a message explaining the error.

        Returns:
            HttpResponse: The HTTP response object with the rendered 403 page.
        """
        message = "You need to be a Superuser to access this view."
        return render(self.request, "403.html", {"message": message})

    def post(self, request, *args, **kwargs):
        # TODO: Update docstring
        """
        Handles the POST request for deleting a user.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: The response after handling the POST request.
        """
        if "Cancel" in request.POST:
            url = self.fail_url
            return redirect(url)
        else:
            return super(DeleteUserView, self).post(request, *args, **kwargs)
