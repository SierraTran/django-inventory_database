from django.urls import path
from . import views

# This is the namespace for the inventory app
app_name = "inventory"

urlpatterns = [
    # URLs for the Item model
    path("items/", views.ItemView.as_view(), name="items"),
    path("items/<int:pk>/", views.ItemDetailView.as_view(), name="item_detail"),    
    # This URL leads to the Item's history (ItemHistory). It needs the id of the current Item object.
    path("items/<int:pk>/history", views.ItemHistoryView.as_view(), name="item_history"),
    # This URL is for creating a new ItemRequest object
    path("items/request", views.ItemRequestCreateView.as_view(), name="item_request_form"), 
    # This URL is for creating a new UsedItem object
    path("items/use", views.UsedItemCreateView.as_view(), name="item_use_form"),
    # These URLs are for creating new Item objects as a Superuser or Technician respectively.
    path("items/new_item_form/superuser", views.ItemCreateSuperuserView.as_view(), name="item_create_form_superuser"),
    path("items/new_item_form/technician", views.ItemCreateTechnicianView.as_view(), name="item_create_form_technician"),
    # These URLs are for updating existing Item objects 
    path("items/<int:pk>/update/superuser", views.ItemUpdateSuperuserView.as_view(), name="item_update_form_superuser"),
    path("items/<int:pk>/update/technician", views.ItemUpdateTechnicianView.as_view(), name="item_update_form_technician"),
    path("items/<int:pk>/update/intern", views.ItemUpdateInternView.as_view(), name="item_update_form_intern"),
    # This URL is for deleting existing Item objects
    path("items/<int:pk>/delete/", views.ItemDeleteView.as_view(), name="item_confirm_delete"),

    path("items/search/", views.SearchItemsView.as_view(), name="search_items"),   
    path("items/import_item_data/", views.ImportItemDataView.as_view(), name="import_item_data"),
    
    # URLs for the ItemRequest model
    path("item_requests/", views.ItemRequestView.as_view(), name="item_requests"),
    path("item_requests/<int:pk>", views.ItemRequestDetailView.as_view(), name="item_request_detail"),
    path("item_requests/<int:pk>/accept", views.ItemRequestAcceptView.as_view(), name="item_request_confirm_accept"),
    path("item_requests/<int:pk>/reject", views.ItemRequestRejectView.as_view(), name="item_request_confirm_reject"),
    path("item_requests/<int:pk>/delete", views.ItemRequestDeleteView.as_view(), name="item_request_confirm_delete"),
    
    # URLs for the UseItem model
    path("used_items/", views.UsedItemView.as_view(), name="used_items"),
    path("used_items/<int:pk>/", views.UsedItemDetailView.as_view(), name="used_item_detail"),
    path("used_items/<int:pk>/delete/", views.UsedItemDeleteView.as_view(), name="used_item_confirm_delete"),
    path("used_items/search/", views.SearchUsedItemsView.as_view(), name="search_used_items"),
    
    # URLs for the PurchaseOrderForm
    path("purchase_order_form/", views.PurchaseOrderItemsFormView.as_view(), name="purchase_order_form")
]
