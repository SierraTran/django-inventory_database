from django.test import Client, TestCase 
from django.urls import reverse
import time_machine
import datetime

from django.contrib.auth.models import User, Group
from inventory.models import Item, ItemHistory


# Create your tests here.


###################################################################################################
# Tests for the Views for the Item Model ##########################################################
###################################################################################################
class ItemViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up initial data.
        """
        items = [
            Item(manufacturer="Fluke", model="Dials", part_or_unit=Item.UNIT, quantity=7),
            Item(manufacturer="Fluke", model="45", part_or_unit=Item.PART, part_number="814137 Rev 2", quantity=1),
            Item(manufacturer="Amprobe", model="Bodys", part_or_unit=Item.PART, part_number="ACDC-100 TRMS", quantity=2),
            Item(manufacturer="Fluke", model="45", part_or_unit=Item.PART, part_number="814137 Rev 102", quantity=1),
            Item(manufacturer="Chroma", part_or_unit=Item.PART, part_number="8-16500016", description="16502 Board", quantity=4, unit_price=341.40),
            Item(manufacturer="HP", model="Handles", part_or_unit=Item.PART, part_number="E3623A", quantity=2),
        ]        
        Item.objects.bulk_create(items)
        
        cls.technician_group = Group.objects.get(name="Technician")
        
        cls.user = User.objects.create_user(username="testuser", password="hayes4800")
        cls.user.groups.add(cls.technician_group)
        
        cls.client = Client()
        cls.items_list_url = reverse("inventory:items")
        
    def test_item_view_GET_unauthenticated(self):
        """
        The ItemView redirects to the login page if the user is unauthenticated.
        """
        response = self.client.get(self.items_list_url, follow=True)
        
        # Make sure the followed response finds the page and uses the right template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")
        
    def test_item_view_GET_authenticated(self):
        """
        The ItemView displays all items in the database for authenticated users.
        """
        self.client.login(username="testuser", password="hayes4800")
        response = self.client.get(self.items_list_url, follow=True)
        
        expected_order = list(Item.objects.all().order_by("manufacturer", "model", "part_number"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "items.html")
        
        # Assert that all items in the database are displayed and in the correct order
        self.assertEqual(len(response.context["items_list"]), Item.objects.count(), "There should be 6 total items.")
        self.assertEqual(list(response.context["items_list"]), expected_order)

    
class ItemDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up initial data.
        """
        cls.item = Item.objects.create(
            manufacturer = "HP",
            model = "Front panel", 
            part_or_unit = Item.PART,
            part_number = "8592E",
            description = "Part for front panel",
            location = "Shelf A2",
            quantity = 3,
            unit_price = 0.75
        )
        
         # Create necessary groups
        cls.viewer_group = Group.objects.get(name="Viewer")
        cls.intern_group = Group.objects.get(name="Intern")
        cls.technician_group = Group.objects.get(name="Technician")
        cls.superuser_group = Group.objects.get(name="Superuser")

        # Create users and assign them to groups
        cls.viewer = User.objects.create_user(username="testviewer", password="hayes4800")
        cls.viewer.groups.add(cls.viewer_group)

        cls.intern = User.objects.create_user(username="testintern", password="hayes4800")
        cls.intern.groups.add(cls.intern_group)

        cls.technician = User.objects.create_user(username="testtechnician", password="hayes4800")
        cls.technician.groups.add(cls.technician_group)

        cls.superuser = User.objects.create_superuser(username="testsuperuser", password="hayes4800")
        cls.superuser.groups.add(cls.superuser_group)
        
        cls.client = Client()
        cls.item_detail_url_valid = reverse("inventory:item_detail", kwargs={"pk": cls.item.pk})
        
    def test_item_detail_GET_unauthenticated(self):
        """
        The ItemDetailView redirects to the login page if the user is unauthenticated.
        """
        response = self.client.get(self.item_detail_url_valid, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")
        
    def test_item_detail_GET_viewer(self):
        """
        The ItemDetailView renders the detail page for the specific item with buttons for Viewers.
        """
        self.client.login(username="testviewer", password="hayes4800")
        response = self.client.get(self.item_detail_url_valid, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "item_detail.html")
        
        # Viewer only has back and history buttons
        self.assertContains(response, '<button type="button" id="back"')
        self.assertContains(response, '<button type="button" id="history"')
        
        # Viewer doesn't have update, use, request more, order more, or delete buttons
        self.assertNotContains(response, '<button type="button" id="update"')
        self.assertNotContains(response, '<button type="button" id="use"')
        self.assertNotContains(response, '<button type="button" id="request-more"')
        self.assertNotContains(response, '<button type="button" id="order-more"')
        self.assertNotContains(response, '<button type="button" class="delete" id="delete"')
        
    def test_item_detail_GET_intern(self):
        """
        The ItemDetailView renders the detail page for the specific item with buttons for Interns.
        """
        self.client.login(username="testintern", password="hayes4800")
        response = self.client.get(self.item_detail_url_valid, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "item_detail.html")
        
        # Interns have back, history, and update buttons
        self.assertContains(response, '<button type="button" id="back"')
        self.assertContains(response, '<button type="button" id="history"')
        self.assertContains(response, '<button type="button" id="update"')
        
        # Intern doesn't have use, request more, order more, or delete buttons        
        self.assertNotContains(response, '<button type="button" id="use"')
        self.assertNotContains(response, '<button type="button" id="request-more"')
        self.assertNotContains(response, '<button type="button" id="order-more"')
        self.assertNotContains(response, '<button type="button" class="delete" id="delete"')
        
    def test_item_detail_GET_Technician(self):
        """
        The ItemDetailView renders the detail page for the specific item with buttons for Technicians.
        """
        self.client.login(username="testtechnician", password="hayes4800")
        response = self.client.get(self.item_detail_url_valid, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "item_detail.html")
        
        # Technician has back, history, update, use, and request more buttons
        self.assertContains(response, '<button type="button" id="back"')
        self.assertContains(response, '<button type="button" id="history"')
        self.assertContains(response, '<button type="button" id="update"')
        self.assertContains(response, '<button type="button" id="use"')
        self.assertContains(response, '<button type="button" id="request-more"')
        self.assertContains(response, '<button type="button" class="delete" id="delete"')
        
        # Technician doesn't have an order more button       
        self.assertNotContains(response, '<button type="button" id="order-more"')  
        
    def test_item_detail_GET_superuser(self):
        """
        The ItemDetailView renders the detail page for the specific item with buttons for Superusers.
        """
        self.client.login(username="testsuperuser", password="hayes4800")
        response = self.client.get(self.item_detail_url_valid, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "item_detail.html")
        
        # Superuser has back, history, update, use, order more, and delete buttons
        self.assertContains(response, '<button type="button" id="back"')
        self.assertContains(response, '<button type="button" id="history"')
        self.assertContains(response, '<button type="button" id="update"')
        self.assertContains(response, '<button type="button" id="use"')
        self.assertContains(response, '<button type="button" id="order-more"')
        self.assertContains(response, '<button type="button" class="delete" id="delete"')
        
        # Superuser doesn't have a request more button        
        self.assertNotContains(response, '<button type="button" id="request-more"', "Superusers should not have a 'Request More' button.")


class ItemCreateSuperuserView(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up for ItemCreateSuperuserView
        
        
class ItemCreateTechnicianView(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up for ItemCreateTechnicianView
    

###################################################################################################
# Tests for the Views for the ItemHistory Model ###################################################
###################################################################################################
class ItemHistoryViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # Assume all users have access to Item History and the button to go to its page.
        # TODO: Set up for ItemHistoryViewTests
        # [ ]: Add an existing item for the user to update
        
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.user.groups.add(cls.superuser_group)
        
        cls.client = Client()       
        
    def test_item_history_view_record_of_creation(self):
        """
        The ItemHistory view shows the record of an item's creation by a user
        
        For records showing no user associated with the creation, see the 
        `test_history_action_create` test function in tests_models.py.
        """
        # User logs in
        login = self.client.login(username="testuser", password="password")
        self.assertTrue(login, "Login failed.")
        
        # User creates an Item
        response = self.client.post(reverse("inventory:item_create_form_superuser"), {
            "manufacturer": "Fluke",
            "model": "N/A",
            "part_or_unit": Item.PART,
            "part_number": "1285578",
            "description": "Power supply connector",
            "location": "Closet",
            "quantity": 3,
            "min_quantity": 0,
            "unit_price": 11.33,
        })
        
        # Check for form erros
        if response.context and 'form' in response.context:
            self.assertFalse(response.context['form'].errors, f"Form errors: {response.context['form'].errors}")
        
        # Make sure the item was created successfully and redirects
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Item.objects.filter(part_number="1285578").exists(), "This item doesn't exist.")
        
        # Check Item History for record of creation        
        item = Item.objects.filter(part_number="1285578").first()
        item_history = ItemHistory.objects.filter(item=item).first()
        
        self.assertIsNotNone(item_history, "The item's history should exist.")
        self.assertEqual(item_history.action, "create", "The action for this record should be 'create'.")
        self.assertEqual(item_history.user, self.user, "The user responsible for the creation should be 'testuser'.")
        
    def test_item_history_view_record_of_update(self):
        """
        The ItemHistory view shows the record of an item's update by a user
        """
        # TODO: test_item_history_view_record_of_update
        # User logs in
        login = self.client.login(username="testuser", password="password")
        self.assertTrue(login, "Login failed.")
        
        # Make sure the item from `setUpTestData` exists
        # self.assertTrue(Item.objects.filter(part_number="1285578").exists(), "This item doesn't exist.")
        
        return 


###################################################################################################
# Tests for the Views for the ItemRequest Model ###################################################
###################################################################################################
class ItemRequestViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up for ItemRequestViewTests

