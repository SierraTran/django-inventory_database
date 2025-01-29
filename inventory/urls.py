from django.urls import path
from . import views

# This is the namespace for the inventory app
app_name = "inventory"

urlpatterns = [
    # example: /inventory_database/items
    path("items/", views.ItemView.as_view(), name="items"),
    # example: /inventory_database/items/9
    path("items/<int:pk>/", views.ItemDetailsView.as_view(), name="item_details"),
]
