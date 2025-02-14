from django.urls import path
from . import views

# This is the namespace for the inventory app
app_name = "inventory"

urlpatterns = [
    # /inventory_database/items
    path("", views.ItemView.as_view(), name="items"),

    # example: /inventory_database/items/9
    path("<int:pk>/", views.ItemDetailView.as_view(), name="item_detail"),
    
    path("<int:pk>/request", views.ItemRequestView.as_view(), name="item_request_form"),
    
    path("<int:pk>/update/", views.ItemUpdateSuperuserView.as_view(), name="item_update_form_superuser"),
    path("<int:pk>/update/", views.ItemUpdateTechnicianView.as_view(), name="item_update_form_technician"),
    path("<int:pk>/update/", views.ItemUpdateInternView.as_view(), name="item_update_form_intern"),
    
    path("<int:pk>/delete/", views.ItemDeleteView.as_view(), name="item_confirm_delete"),
    # /inventory_database/items/new_item_form
    path("new_item_form/", views.ItemCreateSuperuserView.as_view(), name="item_create_form_superuser"),
    path("new_item_form/", views.ItemCreateTechnicianView.as_view(), name="item_create_form_technician"),
    # /inventory_database/items/search
    path("search/", views.SearchItemsView.as_view(), name="search_items"),
    # /inventory_database/items/requests
    path("requests/", views.ItemRequestView.as_view(), name="item_requests"),
    path("import_item_data/", views.ImportItemDataView.as_view(), name="import_item_data"),
]
