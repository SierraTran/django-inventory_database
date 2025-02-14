from django.shortcuts import render, redirect

from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User, Group

from django.urls import reverse_lazy

from django.views.generic import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView

from .models import *


# Create your views here.
def home(request):
    """
    Renders the "home.html" template when the user accesses the home page
    """
    user_group = request.user.groups.first()
    context = {"user_group": user_group}
    return render(request, "home.html", context)


def login_page(request):
    """
    Renders the "login.html" template and handles login logic
    """
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


class UsersView(UserPassesTestMixin, ListView):
    """
    _summary_

    Args:
        UserPassesTestMixin (_type_): _description_
        ListView (_type_): _description_

    Methods:
        test_func(): _description_
        get_queryset(): 
    """
    model = User
    template_name = "users.html"
    context_object_name = "users_list"
    
    def test_func(self) -> bool:
        """
        _summary_

        Returns:
            _description_
        """
        user_group_name = self.request.user.groups.first().name
        return user_group_name == "Superuser"
    
    def get_queryset(self):
        return User.objects.all().order_by("username", "last_name", "first_name")


class UserDetailsView(UserPassesTestMixin, DetailView):
    model = User
    template_name = "user_detail.html"
    
    def test_func(self) -> bool:
        user_group_name = self.request.user.groups.first().name
        return user_group_name == "Superuser"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        specific_user = self.get_object()
        context['user_detail_group_name'] = specific_user.groups.first().name if specific_user.groups.exists() else "No Group"
        return context
    

class CreateUserView(UserPassesTestMixin, CreateView):
    model = User
    fields = ["username", "first_name", "last_name", "email", "password"]
    template_name = "user_create_form.html"
    
    def get_success_url(self):
        return reverse_lazy("authentication:user_details", kwargs={"pk": self.object.pk})
    
    def test_func(self) -> bool:
        user_group_name = self.request.user.groups.first().name
        return user_group_name == "Superuser"

    def form_valid(self, form):
        response = super().form_valid(form)
        group_name = self.request.POST.get("user_group")
        group = Group.objects.get(name=group_name)
        self.object.groups.add(group)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["groups"] = Group.objects.all()
        return context
    

class DeleteUserView(UserPassesTestMixin, DeleteView):
    """
    _summary_

    Returns:
        _description_
    """
    model = User
    success_url = reverse_lazy("authentication:users")
    
    def get_fail_url(self):
        """
        _summary_

        Returns:
            _type_: _description_
        """
        return reverse_lazy("authentication:user_details", kwargs={"pk": self.get_object().pk})

    fail_url = property(get_fail_url)
    
    def test_func(self) -> bool:
        """
        _summary_

        Returns:
            _description_
        """
        user_group_name = self.request.user.groups.first().name
        return user_group_name == "Superuser"
    
    def post(self, request, *args, **kwargs):
        """
        _summary_

        Arguments:
            request -- _description_

        Returns:
            _description_
        """
        if "Cancel" in request.POST:
            url = self.fail_url
            return redirect(url)
        else: 
            return super(DeleteUserView, self).post(request, *args, **kwargs)
    
    # def form_valid(self, form):
    #     messages.success(self.request, "The user was deleted successfully.")
    #     return super(DeleteUserView, self).form_valid(form)


# @login_required
# def logout_view(request):
#     logout(request)
#     return redirect(reverse(home))
