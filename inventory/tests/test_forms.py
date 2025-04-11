from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

import datetime

from django.contrib.auth.models import User, Group
from inventory.models import Item


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
            Item(manufacturer="Test MFG", model="Test Model", part_or_unit=Item.PART, part_number="9876-5432", quantity=5),
            Item(manufacturer="Fluke", model="Knob", part_or_unit=Item.PART, part_number="00129", quantity=3),
        ]
        for item in items: 
            item.save()
            
        cls.item_use_form_url = reverse("inventory:item_use_form")
            
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(Group.objects.get(name="Superuser"))
        
        cls.client = Client()
        
        
    def test___init__no_get_params(self):
        """
        Test that the __init__ function works correctly without get parameters in the url
        """
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.item_use_form_url)
        
        self.assertEqual(response.status_code, 404, "Unexpectedly gained access to the item use form")

        
    def test___init__with_get_params(self):
        """
        Test that the __init__ function works correctly with get parameters in the url
        """
        # TODO: test___init__
        # [x]: GET the form 
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.item_use_form_url+f"?item_id=1")
        
        self.assertEqual(response.status_code, 200, "Failed to access the item use form")

class ItemRequestFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: setUpTestData
        items = [
            Item(manufacturer="Tektronix", model="18934G", part_or_unit=Item.PART, part_number="V9856", quantity=2),            
            Item(manufacturer="HP", model="Main Board", part_or_unit=Item.PART, part_number="1234-5678", quantity=8),
            Item(manufacturer="Test MFG", model="Test Model", part_or_unit=Item.PART, part_number="9876-5432", quantity=5),
            Item(manufacturer="Fluke", model="Knob", part_or_unit=Item.PART, part_number="00129", quantity=3),
        ]
        for item in items: 
            item.save()
            
        cls.item = Item.objects.get(manufacturer="Tektronix", model="18934G", part_number="V9856")
            
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(Group.objects.get(name="Technician"))
        
        cls.item_request_form_url = reverse("inventory:item_request_form")
        
        cls.client = Client()
        
    def test___init__no_get_params(self):
        """
        Test that the __init__ function works correctly without get parameters in the url
        """
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.item_request_form_url)
        
        self.assertEqual(response.status_code, 404, "Unexpectedly gained access to the item use form")
        
    def test___init__with_get_params(self):
        """
        Test that the __init__ function works correctly
        """
        # TODO: test___init__
        # [x]: Make sure the `model_part_num` field label is "Model / Part #"
        self.client.login(username="testuser", password="password")
        response = self.client.get(
            self.item_request_form_url +
            f"?item_id={self.item.id}&manufacturer={self.item.manufacturer}&model_part_num={self.item.model_part_num}&description={self.item.description}&unit_price={self.item.unit_price}"
        )
        
        self.assertEqual(response.status_code, 200, "Failed to access the item request form")
        self.assertNotContains(response, '<th>Model part num</th>')
        self.assertContains(response, '<th>Model / Part #</th>')    
        

class PurchaseOrderItemFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: setUpTestData
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(Group.objects.get(name="Superuser"))
        
        cls.purchase_order_form_url = reverse("inventory:purchase_order_form")
        
        cls.client = Client()
        
    def test___init__(self):
        """
        Test that the __init__ function works correctly
        """        
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.purchase_order_form_url)
        
        self.assertEqual(response.status_code, 200, "Failed to access the purchase order form")
        self.assertContains(response, '-model_part_num">Model / Part #</label>')
        self.assertContains(response, '-serial_num">Serial #</label>')
        self.assertContains(response, '-property_num">Property #</label>')