"""
This module contains the forms used in the inventory app.
"""

from django import forms
from django.forms import modelformset_factory
from .models import Item, UsedItem, ItemRequest, PurchaseOrderItem


class ImportFileForm(forms.Form):
    """
    A form for importing an Excel file containing items to be added to the inventory.
    
    Attributes:
        file (forms.FileField): A file field for uploading the Excel file.
    """
    file = forms.FileField()


class ItemSuperuserForm(forms.ModelForm):
    """
    A form for creating new `Item` objects as a superuser,
    used in ItemCreateSuperuserView and ItemUpdateSuperuserView.
    """

    class Meta:
        """
        Meta class for ItemSuperuserForm
        
        Attributes:
            model (Item): The model associated with this form.
            fields (list[str]): The fields to include in the form.
            labels (dict): The labels for the fields in the form.
        """
        model = Item
        fields = [
            "manufacturer",
            "model",
            "part_or_unit",
            "part_number",
            "description",
            "location",
            "quantity",
            "min_quantity",
            "unit_price",
        ]
        labels = {
            "manufacturer": "Manufacturer",
            "model": "Model",
            "part_or_unit": "Part or Unit",
            "part_number": "Part Number",
            "description": "Description",
            "location": "Storage Location",
            "quantity": "Quantity in Stock",
            "min_quantity": "Minimum Quantity",
            "unit_price": "Unit Price ($)",
        }


class ItemTechnicianForm(forms.ModelForm):
    """
    A form for creating new `Item` objects as a technician, 
    used in ItemCreateTechnicianView and ItemUpdateTechnicianView.
    """

    class Meta:
        """
        Meta class for ItemTechnicianForm
        
        Attributes:
            model (Item): The model associated with this form.
            fields (list[str]): The fields to include in the form.
            labels (dict): The labels for the fields in the form.
        """
        model = Item
        fields = [
            "manufacturer",
            "model",
            "part_or_unit",
            "part_number",
            "description",
            "location",
            "quantity",
            "unit_price",
        ]
        labels = {
            "manufacturer": "Manufacturer",
            "model": "Model",
            "part_or_unit": "Part or Unit",
            "part_number": "Part Number",
            "description": "Description",
            "location": "Storage Location",
            "quantity": "Quantity in Stock",
            "unit_price": "Unit Price ($)",
        }


class UsedItemForm(forms.ModelForm):
    """
    A form for creating new `UsedItem` objects, used in the UsedItemCreateView.

    Fields:
        - item : ForeignKey
            - The item that's been used
        - work_order : IntergerField
            - The work order in which the item was used
        - datetime_used : DateTimeField
            - The date and time in which the item was used
        - used_by : ForeignKey
            - The user that used the item
            
    Methods:
        `__init__()`: Constructor method that initializes the form and sets the label for the 
            `datetime_used` field to "Date & Time used:".
    """

    class Meta:
        """
        Meta class for UsedItemForm
        
        Attributes:
            model (UsedItem): The model associated with this form.
            fields (list): The fields to include in the form.
        """
        model = UsedItem
        fields = [
            "item",
            "work_order",
            "used_by",
        ]

    def __init__(self, *args, **kwargs):
        """
        Constructor method that initializes the form and sets the label for the `datetime_used` 
        field to "Date & Time used:".
        
        Args:
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        super(UsedItemForm, self).__init__(*args, **kwargs)

        self.fields["item"].queryset = Item.objects.order_by(
            "manufacturer", "model", "part_number"
        )
        self.fields["work_order"].label = "Work Order"


class ItemRequestForm(forms.ModelForm):
    """
    A form for creating new `ItemRequest` objects, used in the ItemRequestCreateView.

    Fields:
        - manufacturer : CharField
            - The name of the manufacturer of the requested item.
        - model_part_num : CharField
            - The model and/or part number of the requested item.
        - quantity_requested : IntegerField
            - The quantity of the item being requested
        - description : TextField
            - The description of the item
        - unit_price : DecimalField
            - The unit price of the requested item

    Methods:
        __init__(): Constructor method that initializes the form and sets the label for the 
            `model_part_num` field to "Model / Part #:".
    """

    class Meta:
        """
        Meta class for ItemRequestForm
        
        Attributes:
            model (ItemRequest): The model associated with this form.
            fields (list): The fields to include in the form.
        """
        model = ItemRequest
        fields = [
            "manufacturer",
            "model_part_num",
            "quantity_requested",
            "description",
            "unit_price",
        ]

    def __init__(self, *args, **kwargs):
        """
        Constructor method that initializes the form and sets the label for the `model_part_num`
        field to "Model / Part #:".
        
        Args:
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        super(ItemRequestForm, self).__init__(*args, **kwargs)

        self.fields["model_part_num"].label = "Model / Part #"


class PurchaseOrderItemForm(forms.ModelForm):
    """
    A form for creating new `PurchaseOrderItem` objects, used in the PurchaseOrderItemCreateView.

    Fields:
        - manufacturer : CharField
            - The name of the manufacturer of the item being ordered.
        - model_part_num : CharField
            - The model and/or part number of the item being ordered.
        - quantity_ordered : IntegerField
            - The quantity of the item being ordered.
        - description : TextField
            - The description of the item being ordered.
        - serial_num : CharField
            - The serial number of the item being ordered.
        - property_num : CharField
            - The property number of the item being ordered.
        - unit_price : DecimalField
            - The unit price of the item being ordered. 
            
    Methods:
        `__init__()`: Constructor method that initializes the form and sets the labels for the 
            `model_part_num`, `serial_num`, and `property_num` fields.
    """
    class Meta:
        """
        Meta class for PurchaseOrderItemForm
        
        Attributes:
            model (PurchaseOrderItem): The model associated with this form.
            fields (list): The fields to include in the form.
        """
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
        """
        Constructor method that initializes the form and sets the labels for the `model_part_num`,
        `serial_num`, and `property_num` fields.
        
        Args:
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments         
        """
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
