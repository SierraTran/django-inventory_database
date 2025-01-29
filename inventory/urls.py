from django.urls import path
from . import views

# This is the namespace for the inventory app
app_name = "inventory"

urlpatterns = [
    path('items', views.ItemView.as_view(), name='items'),
    path('items/<int:id>', views.ItemDetailsView.as_view(), name='item_details'),
]