from typing import Any
from django import forms
from django.shortcuts import render, redirect

from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User, Group

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

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered "home.html" template.
    """
    user_group = request.user.groups.first()
    context = {"user_group": user_group}
    return render(request, "home.html", context)


def login_page(request):
    """
    Renders the "login.html" template and handles login logic.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered "login.html" template or a redirect to the home page.
    """
    # Redirect authenticaated users to the home page
    if request.user.is_authenticated:
        return redirect("authentication:home")
    
    # Check if the HTTP request method is POST (form submission)
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check if a user with the provided username exists
        if not User.objects.filter(username=username).exists():
            # Display an error message if the username does not exist
            messages.error(request, "Invalid Username ")
            return redirect("/inventory_database/login/")

        # Authenticate the user with the provided username and password
        user = authenticate(request, username=username, password=password)

        if user is None:
            # Display an error message if authentication fails (invalid password)
            messages.error(request, "Invalid Password ")
            return redirect("/inventory_database/login/")
        else:
            # Log in the user and redirect to the home page upon successful login
            login(request, user)
            return redirect("/inventory_database/")

    # Render the login page template (GET request)
    return render(request, "login.html")


class NotificationsView(LoginRequiredMixin, ListView):
    """
    _summary_

    Attributes:
        LoginRequiredMixin -- _description_
        ListView -- _description_

    """
    
    model = Notification
    template_name = "notifications.html"
    context_object_name = "notifications_list"
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # context[""] = 
        return context
    
    def get_queryset(self):
        current_user = self.request.user
        current_user_notifications = Notification.objects.filter(user=current_user)
        return current_user_notifications
    

class UsersView(UserPassesTestMixin, ListView):
    """
    Displays a list of users.

    Attributes:
        model (User): The model that the view will operate on.
        template_name (str): The template that will be used to render the page.
        context_object_name (str): The context variable name for the list of users.
    """

    model = User
    template_name = "users.html"
    context_object_name = "users_list"

    def test_func(self) -> bool:
        """
        Checks if the user is in the "Superuser" group.

        Returns:
            bool: True if the user is in the "Superuser" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name == "Superuser"

    def get_queryset(self):
        """
        Retrieves all users from the database.

        Returns:
            QuerySet: The queryset containing all users in the database.
        """
        return User.objects.all().order_by("username", "last_name", "first_name")


class UserDetailsView(UserPassesTestMixin, DetailView):
    """
    Displays the details of a specific user.

    Attributes:
        model (User): The model that the view will operate on.
        template_name (str): The template that will be used to render the page.
    """

    model = User
    template_name = "user_detail.html"

    def test_func(self) -> bool:
        """
        Checks if the user is in the "Superuser" group.

        Returns:
            bool: True if the user is in the "Superuser" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name == "Superuser"

    def get_context_data(self, **kwargs):
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

    Attributes:
        model (User): The model that the view will operate on.
        fields (list[str]): The fields to be displayed in the form.
        template_name (str): The template that will be used to render the page.
    """

    model = User
    fields = ["username", "first_name", "last_name", "email", "password"]
    template_name = "user_create_form.html"

    def get_success_url(self):
        """
        Returns the URL to redirect to after a successful form submission.

        Returns:
            str: The URL to redirect to.
        """
        return reverse_lazy(
            "authentication:user_details", kwargs={"pk": self.object.pk}
        )

    def test_func(self) -> bool:
        """
        Checks if the user is in the "Superuser" group.

        Returns:
            bool: True if the user is in the "Superuser" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name == "Superuser"

    def form_valid(self, form):
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

    def get_context_data(self, **kwargs):
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


class UpdateUserView(UserPassesTestMixin, UpdateView):
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
        Checks if the user is in the "SUperuser" group

        Returns:
            bool: True if the user is in the "Superuser" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name == "Superuser"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        return context
    
    def get_success_url(self):
        return reverse("authentication:user_details", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        return super().form_valid(form)


class DeleteUserView(UserPassesTestMixin, DeleteView):
    """
    Handles the deletion of a user.

    Attributes:
        model (User): The model that the view will operate on.
        success_url (str): The URL to redirect to after a successful deletion.
    """

    model = User
    success_url = reverse_lazy("authentication:users")

    def get_fail_url(self):
        """
        Returns the URL to redirect to if the deletion is canceled.

        Returns:
            str: The URL to redirect to.
        """
        return reverse_lazy(
            "authentication:user_details", kwargs={"pk": self.get_object().pk}
        )

    fail_url = property(get_fail_url)

    def test_func(self) -> bool:
        """
        Checks if the user is in the "Superuser" group.

        Returns:
            bool: True if the user is in the "Superuser" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name == "Superuser"

    def post(self, request, *args, **kwargs):
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
