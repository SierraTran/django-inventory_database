from django.urls import path
from . import views

# This is the namespace for the inventory app
app_name = "inventory"

urlpatterns = [
    # urls for the Item model
    path("items/", views.ItemView.as_view(), name="items"),
    path("items/<int:pk>/", views.ItemDetailView.as_view(), name="item_detail"),
    
    # This url leads to the Item's history (ItemHistory). It needs the id of the current Item object.
    path("items/<int:pk>/history", views.ItemHistoryView.as_view(), name="item_history"),
    
    # This url will create an ItemRequest object. It needs the id of the current Item object
    path("items/request", views.ItemRequestCreateView.as_view(), name="item_request_form"),
    
    # This url will create a UsedItem object. It needs the id of the current Item object
    path("items/use", views.UsedItemCreateView.as_view(), name="item_use_form"),
    
    path("items/<int:pk>/update/", views.ItemUpdateSuperuserView.as_view(), name="item_update_form_superuser"),
    path("items/<int:pk>/update/", views.ItemUpdateTechnicianView.as_view(), name="item_update_form_technician"),
    path("items/<int:pk>/update/", views.ItemUpdateInternView.as_view(), name="item_update_form_intern"),
    path("items/<int:pk>/delete/", views.ItemDeleteView.as_view(), name="item_confirm_delete"),
    path("items/new_item_form/", views.ItemCreateSuperuserView.as_view(), name="item_create_form_superuser"),
    path("items/new_item_form/", views.ItemCreateTechnicianView.as_view(), name="item_create_form_technician"),
    path("items/search/", views.SearchItemsView.as_view(), name="search_items"),   
    path("items/import_item_data/", views.ImportItemDataView.as_view(), name="import_item_data"),
    
    # urls for the ItemRequest model
    path("item_requests/", views.ItemRequestView.as_view(), name="item_requests"),
    path("item_requests/<int:pk>", views.ItemRequestDetailView.as_view(), name="item_request_detail"),

    
    # urls for the UseItem model
    path("used_items/", views.UsedItemView.as_view(), name="used_items"),
    path("used_items/<int:pk>/", views.UsedItemDetailView.as_view(), name="used_item_detail"),
    path("used_items/search/", views.SearchUsedItemsView.as_view(), name="search_used_items"),
    
    # 
    path("purchase_order_form/", views.PurchaseOrderItemsFormView.as_view(), name="purchase_order_form")
]
