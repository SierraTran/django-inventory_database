from django import forms
from django.forms import modelformset_factory, formset_factory
from .models import ItemRequest , PurchaseOrderItem

class ImportFileForm(forms.Form):
    file = forms.FileField()
    
class ItemRequestForm(forms.ModelForm):
    class Meta:
        model = ItemRequest
        fields = [
            "item",
            "quantity_requested", 
            "requested_by", 
            "status",
        ]
        


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


