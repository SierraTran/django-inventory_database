from haystack import indexes
from .models import Item

class ItemIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    manufacturer = indexes.CharField(model_attr='manufacturer')
    model = indexes.CharField(model_attr='model')
    part_or_unit = indexes.CharField(model_attr='part_or_unit')
    part_number = indexes.CharField(model_attr='part_number')
    description = indexes.CharField(model_attr='description')
    location = indexes.CharField(model_attr='location')
    quantity = indexes.IntegerField(model_attr='quantity')
    unit_price = indexes.DecimalField(model_attr='unit_price')

    def get_model(self):
        return Item

    def index_queryset(self, using=None):
        return self.get_model().objects.all()