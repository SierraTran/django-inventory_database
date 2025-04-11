import logging
from django.contrib import admin
from .models import Item, ItemHistory, ItemRequest, UsedItem, PurchaseOrderItem
from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)

class ItemAdmin(admin.ModelAdmin):
    # This will list the items on the admin site
    # using the fields `manufacturer`, `model`, and `part_number`
    list_display = [
        "manufacturer",
        "model",
        "part_number",
    ]

    # Items can be filtered for being a part or unit
    list_filter = ["part_or_unit"]

    # Items are alphabetically ordered by manufacturer, model, and then part_number
    ordering = ["manufacturer", "model", "part_number"]


class ItemHistoryAdmin(admin.ModelAdmin):
    list_filter = ["action"]


class ItemRequestAdmin(admin.ModelAdmin):
    # Items can be filtered based on status
    list_filter = ["status"]


class UsedItemAdmin(admin.ModelAdmin):
    list_display = ["work_order", "item"]


class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ["manufacturer", "model_part_num", "quantity_ordered", "description"]


# Register your models here.
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemHistory, ItemHistoryAdmin)
admin.site.register(ItemRequest, ItemRequestAdmin)
admin.site.register(UsedItem, UsedItemAdmin)
admin.site.register(PurchaseOrderItem, PurchaseOrderItemAdmin)
