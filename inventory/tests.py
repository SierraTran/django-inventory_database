from django.test import TestCase

from .models import Item


# Create your tests here.
class ItemModelTests(TestCase):
    def test_create_item_unit(self):
        """
        Test that an item (unit) can be created.
        """
        manufacturer = "Test MFG"
        model = "Test Model"
        part_or_unit = Item.UNIT

        item = Item.objects.create(
            manufacturer=manufacturer, model=model, part_or_unit=part_or_unit
        )
        self.assertTrue(isinstance(item, Item))
        self.assertEqual(item.__str__(), "Test MFG, Test Model")

    def test_create_item_part_blankpartnumber(self):
        """
        Test that an item (part) can be created.
        """
        manufacturer = "Test MFG2"
        model = "Test Model2"
        part_or_unit = Item.PART

        item = Item.objects.create(
            manufacturer=manufacturer, model=model, part_or_unit=part_or_unit
        )
        self.assertTrue(isinstance(item, Item))
        self.assertEqual(item.__str__(), "Test MFG2, Test Model2 ")

    def test_create_item_part_nonblankpartnumber(self):
        """
        Test that an item (part) can be created.
        """
        manufacturer = "Test MFG2"
        model = "Test Model2"
        part_or_unit = Item.PART
        part_number = "Test Part Number"

        item = Item.objects.create(
            manufacturer=manufacturer,
            model=model,
            part_or_unit=part_or_unit,
            part_number=part_number,
        )
        self.assertTrue(isinstance(item, Item))
        self.assertEqual(item.__str__(), "Test MFG2, Test Model2 Test Part Number")

    def test_item_quantity(self):
        """
        Test that the item quantity is correct.
        """
        item = Item.objects.create(quantity=20)
        self.assertEqual(item.quantity, 20)

    def test_item_unit_price(self):
        """
        Test that the item unit price is correct.
        """
        item = Item.objects.create(unit_price=200.0)
        self.assertEqual(item.unit_price, 200.0)
