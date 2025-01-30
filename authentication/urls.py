from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [
    path('', views.home, name='home'),
    #path('login/', views.login_page, name='login'),
    #path('logout/', views.logout_view, name="logout"),
]