from django.urls import path
from . import views

urlpatterns = [
    path('items', views.items, name='items'),
    path('items/more_info/<int:id>', views.more_info, name='more_info'),
]