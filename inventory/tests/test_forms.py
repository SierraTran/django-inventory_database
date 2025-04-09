from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase, tag
from django.urls import reverse
from django.utils import timezone

import time_machine
import datetime

from django.contrib.auth.models import User, Group
from inventory.models import Item
from inventory.forms import UsedItemForm, ItemRequestForm, PurchaseOrderItemForm



# Create your tests here.

class UsedItemFormTests(TestCase):
    # NOTE: Local date and time is set to January 3, 2025 at 1:00 PM for testing purposes
    aware_datetime = timezone.make_aware(datetime.datetime(2025, 1, 3, 13, 0, 0))
    
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: setUpTestData
        # [ ]: Make several different (available) items
        # [ ]: Create a user for using the items
        # [ ]: Set time for the tests
        
        items = [
            Item(manufacturer="Tektronix", model="18934G", part_or_unit=Item.PART, part_number="V9856", quantity=2),            
            Item(manufacturer="HP", model="Main Board", part_or_unit=Item.PART, part_number="1234-5678", quantity=8),
                       
        ]
        Item.objects.bulk_create(items)
        
    def test___init__(self):
        """
        Test that the __init__ function works correctly
        """
        # TODO: test___init__
        # [ ]: Initiate the form 
        # [ ]: Make sure the item choices are in the expected order
        # [ ]: make sure the `datetime_used` field label is "Date & Time used:"
        
        form = UsedItemForm()
        

class ItemRequestFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: setUpTestData
        
    def test___init__(self):
        """
        Test that the __init__ function works correctly
        """
        # TODO: test___init__
        # [ ]: Make sure the `model_part_num` field label is "Model / Part #:"


class PurchaseOrderItemFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: setUpTestData
        
    def test___init__(self):
        """
        Test that the __init__ function works correctly
        """
        # TODO: test___init__
        # [ ]: The `model_part_num` field label is "Model / Part #:"
        # [ ]: The `serial_num` field label is "Serial #"
        # [ ]: The `property_num` field label is "Property #"