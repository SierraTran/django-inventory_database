from django.contrib import admin
from .models import Item, ItemRequest


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

class ItemRequestAdmin(admin.ModelAdmin):
    # Items can be filtered based on status
    list_filter = ["status"]

# Register your models here.
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemRequest, ItemRequestAdmin)
