from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
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


# @login_required
# def logout_view(request):
#     logout(request)
#     return redirect(reverse(home))
