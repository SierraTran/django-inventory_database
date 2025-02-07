from django.urls import path
from . import views

# This is the namespace for the inventory app
app_name = "inventory"

urlpatterns = [
    # example: /inventory_database/items
    path("", views.ItemView.as_view(), name="items"),
    # example: /inventory_database/items/9
    path("<int:pk>/", views.ItemDetailView.as_view(), name="item_detail"),
    path("new_item_form/", views.ItemCreateView.as_view(), name="item_create_form"),
    path("<int:pk>/update", views.ItemUpdateView.as_view(), name="item_update_form"),
    path("<int:pk>/quantity_update", views.ItemQuantityUpdateView.as_view(), name="item_quantity_update_form"),
    path('search/', views.SearchItemsView.as_view(), name='search_items'),
]
