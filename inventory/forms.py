from django import forms
from django.forms import modelformset_factory, formset_factory
from .models import PurchaseOrderItem

class ImportFileForm(forms.Form):
    file = forms.FileField()

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


PurchaseOrderItemFormSet = modelformset_factory(
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=1,
    can_delete=True,
)


