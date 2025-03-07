from django import forms
from django.forms import modelformset_factory
from django.contrib.auth.models import User, Group
from .models import Item, UsedItem, ItemRequest, PurchaseOrderItem


class ImportFileForm(forms.Form):
    file = forms.FileField()
    
class UsedItemForm(forms.ModelForm):
    class Meta:
        model = UsedItem
        fields = [
            "item",
            "work_order",
            "datetime_used",
            "used_by",
        ]
        
    def __init__(self, *args, **kwargs):
        super(UsedItemForm, self).__init__(*args, **kwargs)
        
        self.fields["item"].queryset = Item.objects.order_by("manufacturer", "model", "part_number")
        self.fields["datetime_used"].label = "Date & Time used:"
        # FIXME: This filter isn't working?
        self.fields["used_by"].queryset = User.objects.filter(groups__name__in=["Technician", "Superuser"])


class ItemRequestForm(forms.ModelForm):
    class Meta:
        model = ItemRequest
        fields = [
            "manufacturer",
            "model_part_num",
            "quantity_requested",
            "description",
            "unit_price",
            "requested_by",
        ]
        
    def __init__(self, *args, **kwargs):
        super(UsedItemForm, self).__init__(*args, **kwargs)
        
        # FIXME: This filter isn't working?
        self.fields["requested_by"].queryset = User.objects.filter(groups__name="Technician")
        self.fields["model_part_num"].label = "Model / Part #:"
        
        


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = [
            "manufacturer",
            "model_part_num",
            "quantity_ordered",
            "description",
            "serial_num",
            "property_num",
            "unit_price",
        ]

    def __init__(self, *args, **kwargs):        
        super(PurchaseOrderItemForm, self).__init__(*args, **kwargs)

        self.fields["model_part_num"].label = "Model / Part #"
        self.fields["serial_num"].label = "Serial #"
        self.fields["property_num"].label = "Property #"

            


ItemRequestFormSet = modelformset_factory(
    ItemRequest,
    form=ItemRequestForm,
    extra=1,
    can_delete=True,
)

PurchaseOrderItemFormSet = modelformset_factory(
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=1,
    can_delete=True,
)
