"""
This module contains the search indexes for the inventory app's models.
"""

from haystack import indexes
from .models import Item, UsedItem

class ItemIndex(indexes.SearchIndex, indexes.Indexable):
    """
    This class defines the search index for the Item model.

    Fields:
        - text: The full text search field, which uses a template to generate the content.
        - manufacturer: The manufacturer of the item.
        - model: The model of the item.
        - part_or_unit: The part or unit of the item.
        - part_number: The part number of the item.
        - description: A description of the item.
        - location: The location of the item.
        - quantity: The quantity of the item in stock.
        - unit_price: The unit price of the item.

    Methods:
        - get_model: Returns the model class for this index.
        - index_queryset: Returns the queryset to be indexed.
    """
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

class UsedItemIndex(indexes.SearchIndex, indexes.Indexable):
    """
    This class defines the search index for the UsedItem model.

    Fields:
        - text: The full text search field, which uses a template to generate the content.
        - item: The item associated with the used item.
        - work_order: The work order associated with the used item.

    Methods:
        - get_model: Returns the model class for this index.
        - index_queryset: Returns the queryset to be indexed.
    """
    text = indexes.CharField(document=True, use_template=True)
    item = indexes.CharField(model_attr='item')
    work_order = indexes.IntegerField(model_attr='work_order')

    def get_model(self):
        return UsedItem

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
