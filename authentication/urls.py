from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [
    path("", views.home, name="home"),
    path("new_account_form/", views.CreateAccountView.as_view(), name="user_create_form"),
]
