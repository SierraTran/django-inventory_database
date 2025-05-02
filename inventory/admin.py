"""
This module defines the admin interface for the inventory app.
It customizes the admin views for the Item, ItemHistory, ItemRequest, UsedItem, and 
PurchaseOrderItem models.
"""
import logging
from django.contrib import admin
from .models import Item, ItemHistory, ItemRequest, UsedItem, PurchaseOrderItem

logger = logging.getLogger(__name__)


class ItemAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the Item model.

    Attributes:
        list_display (list): Fields to display in the admin list view.
            - manufacturer: The manufacturer of the item.
            - model: The model of the item.
            - part_number: The part number of the item.
        list_filter (list): Fields to filter the list view.
            - part_or_unit: Filter items by whether they are a part or unit.
        ordering (list): Default ordering of items in the list view.
            - manufacturer: Order by manufacturer.
            - model: Then order by model.
            - part_number: Finally order by part number.
    """

    list_display = [
        "manufacturer",
        "model",
        "part_number",
    ]
    list_filter = ["part_or_unit"]
    ordering = ["manufacturer", "model", "part_number"]


class ItemHistoryAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the ItemHistory model.
    
    Attributes:
        list_filter (list): Fields to filter the list view.
            - action: Filter the item history by the action that was taken.
    """
    list_filter = ["action"]


class ItemRequestAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the ItemRequest model.
    
    Attributes:
        list_filter (list): Fields to filter the list view.
            - status: Filter the item requests by their current status.
    """
    list_filter = ["status"]


class UsedItemAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the UsedItem model.
    
    Attributes:
        list_display (list): Fields to display in the admin list view.
            - work_order: The work order of the used item.
            - item: The item that was used.
    """
    list_display = ["work_order", "item"]


class PurchaseOrderItemAdmin(admin.ModelAdmin):
    """
    Custom admin interface for th PurchaseOrderItem model.
    
    Attributes:
        list_display (list): Fields to display in the admin list view.
            - manufacturer: The manufacturer of the item.
            - model_part_num: The model and/or part number of the item.
            - quantity_ordered: The quantity being ordered.
            - description: The description of the item.
            
    """
    list_display = ["manufacturer", "model_part_num", "quantity_ordered", "description"]


# Register your models here.
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemHistory, ItemHistoryAdmin)
admin.site.register(ItemRequest, ItemRequestAdmin)
admin.site.register(UsedItem, UsedItemAdmin)
admin.site.register(PurchaseOrderItem, PurchaseOrderItemAdmin)
