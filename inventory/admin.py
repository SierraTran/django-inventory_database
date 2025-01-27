from django.contrib import admin
from .models import Item


class ItemAdmin(admin.ModelAdmin):
    # This will list the items on the admin site 
    # using the fields `manufacturer`, `model`, and `part_number`
    list_display = ["manufacturer", "model", "part_number"]

    list_filter = ["part_or_unit"]


# Register your models here.
admin.site.register(Item, ItemAdmin)
