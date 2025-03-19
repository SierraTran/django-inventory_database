# TODO: Module docstring

from django import forms
from django.forms import modelformset_factory
from django.contrib.auth.models import User, Group
from .models import Item, UsedItem, ItemRequest, PurchaseOrderItem


class ImportFileForm(forms.Form):
    file = forms.FileField()
    
class UsedItemForm(forms.ModelForm):
    # TODO: Class docstring
    class Meta:
        model = UsedItem
        fields = [
            "item",
            "work_order",
            "datetime_used",
            "used_by",
        ]
        
    def __init__(self, *args, **kwargs):
        # TODO: Method docstring
        super(UsedItemForm, self).__init__(*args, **kwargs)
        
        self.fields["item"].queryset = Item.objects.order_by("manufacturer", "model", "part_number")
        self.fields["datetime_used"].label = "Date & Time used:"


class ItemRequestForm(forms.ModelForm):
    """
    A form for creating new `ItemRequest` objects, used in the ItemRequestCreateView.

    Fields:
        - manufacturer : CharField
            The name of the manufacturer of the requested item.
        - model_part_num : CharField
            The model and/or part number of the requested item.
        - quantity_requested : IntegerField
        - description : TextField
        - unit_price : DecimalField
        - requested_by : ForeignKey

    Methods:
        __init__(): Constructor method that initializes the form and sets the label for the `model_part_num` field tp "Model / Part #:".
    """

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
        # TODO: Method docstring
        super(UsedItemForm, self).__init__(*args, **kwargs)

        self.fields["model_part_num"].label = "Model / Part #:"
        
        


class PurchaseOrderItemForm(forms.ModelForm):
    # TODO: Class docstring
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
        # TODO: Method docstring        
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
