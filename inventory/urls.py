from django.urls import path
from . import views

# This is the namespace for the inventory app
app_name = "inventory"

urlpatterns = [
    # example: /inventory_database/items
    path("", views.ItemView.as_view(), name="items"),
    # example: /inventory_database/items/9
    #path("items/<int:pk>/", views.getItemDetails, name="item_details"), [OLD]
    path("<int:pk>/", views.ItemDetailView.as_view(), name="item_detail"),
    #path("items/<int:pk>/update", views.updateItemAsSuperuser, name="update-item-superuser"), [OLD]
    path("<int:pk>/update", views.ItemUpdateView.as_view(), name="item_update_form"),
    path("<int:pk>/quantity_update", views.ItemQuantityUpdateView.as_view(), name="item_quantity_update_form"),
    path('search/', views.search_items, name='search_items'),
]
