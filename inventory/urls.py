from django.urls import path
from . import views

# This is the namespace for the inventory app
app_name = "inventory"

urlpatterns = [
    # /inventory_database/items
    path("", views.ItemView.as_view(), name="items"),
    # /inventory_database/items/requests
    path("requests/", views.ItemRequestView.as_view(), name="item_requests"),
    # example: /inventory_database/items/9
    path("<int:pk>/", views.ItemDetailView.as_view(), name="item_detail"),
    path("<int:pk>/request", views.ItemRequestView.as_view(), name="item_request_form"),
    # /inventory_database/items/new_item_form
    path("new_item_form/", views.ItemCreateView.as_view(), name="item_create_form"),
    path("<int:pk>/superusers_update", views.ItemUpdateSuperuserView.as_view(), name="item_update_form_superuser"),
    path("<int:pk>/technicians_update", views.ItemUpdateTechnicianView.as_view(), name="item_update_form_technician"),
    path("<int:pk>/interns_update", views.ItemUpdateInternView.as_view(), name="item_update_form_intern"),
    # /inventory_database/items/search
    path("search/", views.SearchItemsView.as_view(), name="search_items"),
]
