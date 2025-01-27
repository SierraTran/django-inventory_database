from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path('items', views.items, name='items'),
    path('items/more_info/<int:id>', views.more_info, name='more_info'),
]