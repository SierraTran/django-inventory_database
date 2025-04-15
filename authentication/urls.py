from django.urls import path
from . import views, context_processors

app_name = "authentication"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.DatabaseLoginView.as_view(), name="login"),
    
    # URLs for the Notification model
    path("notifications", views.NotificationView.as_view(), name="notifications"),
    path('notifications/unread_count/', views.unread_notifications_count_view, name='unread_notifications_count'),
    path("notifications/<int:pk>/update", views.NotificationUpdateView.as_view(), name="notification_update_form"),
    path("notifications/<int:pk>/delete", views.NotificationDeleteView.as_view(), name="notification_confirm_delete"),
    
    # URLs for the User model
    path("new_user_form/", views.UserCreateView.as_view(), name="user_create_form"),
    path("users/", views.UsersView.as_view(), name="users"),
    path("users/<int:pk>", views.UserDetailsView.as_view(), name="user_details"),
    path("users/<int:pk>/update", views.UserUpdateView.as_view(), name="user_update_form"),
    path("users/<int:pk>/delete", views.UserDeleteView.as_view(), name="user_confirm_delete"),
]
