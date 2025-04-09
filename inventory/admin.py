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

    # def delete_model(self, request, obj):
    #     """
    #     Overrides the delete_model method to handle IntegrityError.

    #     Args:
    #         request (HttpRequest): The HTTP request object.
    #         obj (Item): The item object to be deleted.
    #     """
    #     try:
    #         # Log related records before deletion
    #         logger.info(f"Deleting ItemHistory records for item {obj.id}")
    #         ItemHistory.objects.filter(item=obj).delete()
    #         logger.info(f"Deleting ItemRequest records for item {obj.id}")
    #         ItemRequest.objects.filter(item=obj).delete()
    #         logger.info(f"Deleting UsedItem records for item {obj.id}")
    #         UsedItem.objects.filter(item=obj).delete()

    #         # Delete the item
    #         logger.info(f"Deleting item {obj.id}")
    #         obj.delete()
    #         messages.success(
    #             request, "The item and its related records were deleted successfully."
    #         )
    #     except IntegrityError as e:
    #         logger.error(f"IntegrityError: {e}")
    #         messages.error(
    #             request,
    #             "Cannot delete this item because it is referenced by other records.",
    #         )
    #         return redirect("admin:inventory_item_changelist")

    # def delete_view(self, request, object_id, extra_context=None):
    #     """
    #     Overrides the delete_view method to handle IntegrityError.

    #     Args:
    #         request (HttpRequest): The HTTP request object.
    #         object_id (str): The ID of the object to be deleted.
    #         extra_context (dict): Additional context data for the view.

    #     Returns:
    #         HttpResponse: The HTTP response object.
    #     """
    #     try:
    #         return super().delete_view(request, object_id, extra_context)
    #     except IntegrityError:
    #         messages.error(
    #             request,
    #             "Cannot delete this item because it is referenced by other records.",
    #         )
    #         return redirect(reverse("admin:inventory_item_changelist"))


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
