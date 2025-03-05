from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [
    path("", views.home, name="home"),
    path("notifications", views.NotificationsView.as_view(), name="notifications"),
    path("new_user_form/", views.CreateUserView.as_view(), name="user_create_form"),
    path("users/", views.UsersView.as_view(), name="users" ),
    path("users/<int:pk>", views.UserDetailsView.as_view(), name="user_details"),
    path("users/<int:pk>/update", views.UpdateUserView.as_view(), name="user_update_form"),
    path("users/<int:pk>/delete", views.DeleteUserView.as_view(), name="user_confirm_delete"),
]
