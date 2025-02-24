from django import forms

from .models import PurchaseOrderItem


class ImportFileForm(forms.Form):
    file = forms.FileField()


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["model_part_num"].label = "Model / Part #"

        self.fieldset = PurchaseOrderItemFormSet()


PurchaseOrderItemFormSet = forms.formset_factory(PurchaseOrderItemForm, extra=1)
