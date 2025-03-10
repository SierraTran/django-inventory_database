from django.test import TestCase

from .models import Item


# Create your tests here.
class ItemModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.item1 = Item.objects.create(
            manufacturer="Test MFG1",
            model="Test Model1",
            part_or_unit=Item.UNIT,
            quantity=1,
            unit_price=100.00,
        )
        cls.item2 = Item.objects.create(
            manufacturer="Test MFG2",
            model="Test Model2",
            part_or_unit=Item.PART,
            quantity=5,
            min_quantity=10,
            unit_price=0.50,
        )
        cls.item3 = Item.objects.create(
            manufacturer="Test MFG3",
            model="Test Model3",
            part_or_unit=Item.PART,
            part_number="Test Part Number",
        )

    def test_item_unit(self):
        """
        Test that an item (unit) can be created.
        """
        self.assertTrue(isinstance(self.item1, Item))
        self.assertEqual(self.item1.__str__(), "Test MFG1, Test Model1")

    def test_create_item_part_blankpartnumber(self):
        """
        Test that an item (part) can be created without a part number.
        """
        self.assertTrue(isinstance(self.item2, Item))
        self.assertEqual(self.item2.__str__(), "Test MFG2, Test Model2 ")

    def test_create_item_part_nonblankpartnumber(self):
        """
        Test that an item (part) can be created with a part number.
        """
        self.assertTrue(isinstance(self.item3, Item))
        self.assertEqual(
            self.item3.__str__(), "Test MFG3, Test Model3 Test Part Number"
        )

    def test_item_quantity1(self):
        """
        Test that the item quantity is correct.
        
        For the first item, this should be 1.
        """
        self.assertEqual(self.item1.quantity, 1)
        
    def test_item_quantity2(self):
        """
        Test that the item quantity is correct.
        
        For the second item, this should be 5.
        """
        self.assertEqual(self.item2.quantity, 5)
        
    def test_item_quantity3(self):
        """
        Test that the item quantity is correct.
        
        For the third item, this should be 0 as it was not specified upon creation.
        """
        self.assertEqual(self.item3.quantity, 0)
        
    def test_item_is_low_stock(self):
        """
        Test that an item low in stock has its property `low_stock` set as True.
        """
        self.assertTrue(self.item2.low_stock)
        
    def test_item_is_not_low_stock(self):
        """
        Test that an item not low in stock has its property `low_stock` set as False.
        """
        self.assertFalse(self.item1.low_stock)

    def test_item_unit_price1(self):
        """
        Test that the item unit price is correct.
        
        For the first item, this should be 100.00.
        """
        self.assertEqual(self.item1.unit_price, 100.00)
        
    def test_item_unit_price2(self):
        """
        Test that the item unit price is correct.
        
        For the second item, this should be 0.50.
        """
        self.assertEqual(self.item2.unit_price, 0.50)

    def test_item_unit_price3(self):
        """
        Test that the item unit price is correct.
        
        For the third item, this should be 0.01 as no unit price has been specified.
        """
        self.assertEqual(float(self.item3.unit_price), 0.01)

    def test_item_model_part_num1(self):
        """
        Test that the `model_part_num` property is correctly set.
        
        For the first item, this should be "Test Model1 ". (Space included because it's a unit.)
        """
        self.assertEqual(self.item1.model_part_num, "Test Model1 ")
        
    def test_item_model_part_num2(self):
        """
        Test that the `model_part_num` property is correctly set.
        
        For the second item, this should be "Test Model2 ". (Space include because no part number has been specified.)
        """
        self.assertEqual(self.item2.model_part_num, "Test Model2 ")
        
    def test_item_model_part_num3(self):
        """
        Test that the `model_part_num` property is correctly set.
        
        For the third item, this should be "Test Model3 Test Part Number".
        """
        self.assertEqual(self.item3.model_part_num, "Test Model3 Test Part Number")
        

# class ItemHistoryModelTests(TestCase):
    # TODO: ItemHistory tests
    # def setUp(self):
    #     """
    #     Set up for ItemHistoryModelTests
    #     """
    #     Item.objects.create(
    #         manufacturer="Test MFG1",
    #         model="Test Model1",
    #         part_or_unit=Item.UNIT,
    #         quantity=1,
    #         unit_price=100.00,
    #     )
    #     Item.objects.create(
    #         manufacturer="Test MFG2",
    #         model="Test Model2",
    #         part_or_unit=Item.PART,
    #         quantity=5,
    #         min_quantity=10,
    #         unit_price=0.50,
    #     )
    #     Item.objects.create(
    #         manufacturer="Test MFG3",
    #         model="Test Model3",
    #         part_or_unit=Item.PART,
    #         part_number="Test Part Number",
    #     )
    #     return

    # def test_history_action_create(self):
    #     """
    #     Make sure the created items have a history record of being created.
    #     """
    #     item1 = Item.objects.filter(manufacturer="Test MFG1")[0]
    #     item2 = Item.objects.filter(manufacturer="Test MFG2")[0]
    #     item3 = Item.objects.filter(manufacturer="Test MFG3")[0]


# class ItemRequestModelTests(TestCase):
#     # TODO: ItemRequest tests
#     def test_none():
#         return


# class UsedItemModelTests(TestCase):
#     # TODO: UsedItem tests
#     def test_none():
#         return
