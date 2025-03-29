from django.test import Client, TestCase, tag
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
        
         # Get necessary groups
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
        self.assertNotContains(response, '<button type="button" id="request-more"')


class ItemCreateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.technician_group = Group.objects.get(name="Technician")
        cls.intern_group = Group.objects.get(name="Intern")
        cls.viewer_group = Group.objects.get(name="Viewer")

        # Create users and assign them to groups
        cls.superuser = User.objects.create_superuser(username="testsuperuser", password="hayes4800")
        cls.superuser.groups.add(cls.superuser_group)
        
        cls.technician = User.objects.create_user(username="testtechnician", password="hayes4800")
        cls.technician.groups.add(cls.technician_group)
        
        cls.intern = User.objects.create_user(username="testintern", password="hayes4800")
        cls.intern.groups.add(cls.intern_group)
        
        cls.viewer = User.objects.create_user(username="testviewer", password="hayes4800")
        cls.viewer.groups.add(cls.viewer_group)

        cls.item_create_superuser_url = reverse("inventory:item_create_form_superuser")
        cls.item_create_technician_url = reverse("inventory:item_create_form_technician")

        cls.client = Client()
    
    @tag("critical")
    def test_item_create_superuser_view_access_control(self):
        """
        Verify that only superusers can access the superuser item creation view.
        """
        self.client.login(username="testsuperuser", password="hayes4800")
        response = self.client.get(self.item_create_superuser_url)
        self.assertEqual(response.status_code, 200, "Superuser failed to access their own view.")
        self.client.logout()
        
        self.client.login(username="testtechnician", password="hayes4800")
        response = self.client.get(self.item_create_superuser_url)
        self.assertEqual(response.status_code, 403, "Technician unexpectedly gained access to superuser view.")
        self.client.logout()
        
        self.client.login(username="testintern", password="hayes4800")
        response = self.client.get(self.item_create_superuser_url)
        self.assertEqual(response.status_code, 403, "Intern unexpectedly gained access to superuser view.")
        self.client.logout()
        
        self.client.login(username="testviewer", password="hayes4800")
        response = self.client.get(self.item_create_superuser_url)
        self.assertEqual(response.status_code, 403, "Viewer unexpectedly gained access to superuser view.")
        self.client.logout()
     
    @tag("critical")   
    def test_item_create_technician_view_access_control(self):
        """
        Verify that only technicians can access the technician item creation view.
        """
        self.client.login(username="testsuperuser", password="hayes4800")
        response = self.client.get(self.item_create_technician_url)
        self.assertEqual(response.status_code, 403, "Superuser unexpectedly gained access to technician view.")
        self.client.logout()
        
        self.client.login(username="testtechnician", password="hayes4800")
        response = self.client.get(self.item_create_technician_url)
        self.assertEqual(response.status_code, 200, "Technician failed to access their own view.")
        self.client.logout()
        
        self.client.login(username="testintern", password="hayes4800")
        response = self.client.get(self.item_create_technician_url)
        self.assertEqual(response.status_code, 403, "Intern unexpectedly gained access to technician view.")
        self.client.logout()
        
        self.client.login(username="testviewer", password="hayes4800")
        response = self.client.get(self.item_create_technician_url)
        self.assertEqual(response.status_code, 403, "Viewer unexpectedly gained access to technician view.")
        self.client.logout()
            
    def test_item_create_as_superuser(self):
        """
        Make sure superusers can create items with only their own dedicated create view.
        """
        # Superuser logins in
        login = self.client.login(username="testsuperuser", password="hayes4800")
        self.assertTrue(login, "Login failed.")

        # Superuser creates an item in their dedicated view
        response = self.client.post(reverse("inventory:item_create_form_superuser"), {
            "manufacturer": "Superuser",
            "model": "Superuser\'s Item",
            "part_or_unit": Item.UNIT,
            # "part_number" is blank since it's a unit
            "description": "Item created by the Superuser",
            "location": "N/A",
            "quantity": 1,
            "min_quantity": 0,
            "unit_price": 0.01,
        })
        
        # Check for form errors
        if response.context and 'form' in response.context:
            self.assertFalse(response.context['form'].errors, f"Form errors: {response.context['form'].errors}")
        
        # Make sure the item was created successfully and redirects
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Item.objects.filter(model="Superuser\'s Item").exists(), "This item doesn't exist.")
    
    def test_item_create_as_technician(self):
        """
        Make sure technicians can create items with only their own dedicated create view.
        """
        login = self.client.login(username="testtechnician", password="hayes4800")
        self.assertTrue(login, "Login failed.")
        
        # Technician creates an item in their dedicated view
        response = self.client.post(reverse("inventory:item_create_form_technician"), {
            "manufacturer": "Technician",
            "model": "Technician\'s Item",
            "part_or_unit": Item.UNIT,
            # "part_number" is blank since it's a unit
            "description": "Item created by the Technician",
            "location": "N/A",
            "quantity": 1,
            # Technicians cannot set the min_quantity
            "unit_price": 0.01,
        })
        
        # Check for form errors
        if response.context and 'form' in response.context:
            self.assertFalse(response.context['form'].errors, f"Form errors: {response.context['form'].errors}")
        
        # Make sure the item was created successfully and redirects
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Item.objects.filter(model="Technician\'s Item").exists(), "This item doesn't exist.")
    
    def test_item_create_as_intern(self):
        """
        Make sure interns can't create items.
        """
        login = self.client.login(username="testintern", password="hayes4800")
        self.assertTrue(login, "Login failed.")
            
        # Attempt to create an item with the superuser's view
        response = self.client.post(reverse("inventory:item_create_form_superuser"), {
            "manufacturer": "Intern",
            "model": "Intern\'s Item",
            "part_or_unit": Item.UNIT,
            # "part_number" is blank since it's a unit
            "description": "Item created by the Intern",
            "location": "N/A",
            "quantity": 1,
            "min_quantity": 0,
            "unit_price": 0.01,
        })
        
        # Check for form errors
        if response.context and 'form' in response.context:
            self.assertFalse(response.context['form'].errors, f"Form errors: {response.context['form'].errors}")
        
        # The item shouldn't exist in the database
        self.assertFalse(Item.objects.filter(model="Intern\'s Item").exists(), "This item does exist.")
        
        # Attempt to create an item with the technician's view
        response = self.client.post(reverse("inventory:item_create_form_technician"), {
            "manufacturer": "Intern",
            "model": "Intern\'s Item",
            "part_or_unit": Item.UNIT,
            # "part_number" is blank since it's a unit
            "description": "Item created by the Intern",
            "location": "N/A",
            "quantity": 1,
            # Technicians cannot set the min_quantity
            "unit_price": 0.01,
        })
        
        # Check for form errors
        if response.context and 'form' in response.context:
            self.assertFalse(response.context['form'].errors, f"Form errors: {response.context['form'].errors}")
        
        # The item shouldn't exist in the database
        self.assertFalse(Item.objects.filter(model="Intern\'s Item").exists(), "This item does exist.")
    
    def test_item_create_as_viewer(self):
        """
        Make sure viewers can't create items.
        """
        login = self.client.login(username="testviewer", password="hayes4800")
        self.assertTrue(login, "Login failed.")
        
        # Attempt to create an item with the superuser's view
        response = self.client.post(reverse("inventory:item_create_form_superuser"), {
            "manufacturer": "Viewer",
            "model": "Viewer\'s Item",
            "part_or_unit": Item.UNIT,
            # "part_number" is blank since it's a unit
            "description": "Item created by the Intern",
            "location": "N/A",
            "quantity": 1,
            "min_quantity": 0,
            "unit_price": 0.01,
        })
        
        # Check for form errors
        if response.context and 'form' in response.context:
            self.assertFalse(response.context['form'].errors, f"Form errors: {response.context['form'].errors}")
        
        # The item shouldn't exist in the database
        self.assertFalse(Item.objects.filter(model="Viewer\'s Item").exists(), "This item does exist.")
        
        # Attempt to create an item with the technician's view
        response = self.client.post(reverse("inventory:item_create_form_technician"), {
            "manufacturer": "Viewer",
            "model": "Viewer\'s Item",
            "part_or_unit": Item.UNIT,
            # "part_number" is blank since it's a unit
            "description": "Item created by the Intern",
            "location": "N/A",
            "quantity": 1,
            # Technicians cannot set the min_quantity
            "unit_price": 0.01,
        })
        
        # Check for form errors
        if response.context and 'form' in response.context:
            self.assertFalse(response.context['form'].errors, f"Form errors: {response.context['form'].errors}")

        # The item shouldn't exist in the database
        self.assertFalse(Item.objects.filter(model="Viewer\'s Item").exists(), "This item does exist.")
    
    
class ItemUpdateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # TODO: Set up for ItemUpdateViewTests
        """
        Setup
        """
        return
    
    def test_item_update_as_superuser(self):
        # TODO: test_item_update_as_superuser
        return 
    
    def test_item_update_as_technician(self):
        # TODO: test_item_update_as_technician
        return 
    
    def test_item_update_as_intern(self):
        # TODO: test_item_update_as_intern
        return 
    
    def test_item_update_as_viewer(self):
        # TODO: test_item_update_as_viewer
        return 


class ItemDeleteViewtests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.technician_group = Group.objects.get(name="Technician")
        cls.intern_group = Group.objects.get(name="Intern")
        cls.viewer_group = Group.objects.get(name="Viewer")

        # Create users and assign them to groups
        cls.superuser = User.objects.create_superuser(username="testsuperuser", password="hayes4800")
        cls.superuser.groups.add(cls.superuser_group)
        
        cls.technician = User.objects.create_user(username="testtechnician", password="hayes4800")
        cls.technician.groups.add(cls.technician_group)
        
        cls.intern = User.objects.create_user(username="testintern", password="hayes4800")
        cls.intern.groups.add(cls.intern_group)
        
        cls.viewer = User.objects.create_user(username="testviewer", password="hayes4800")
        cls.viewer.groups.add(cls.viewer_group)
        
        cls.superuser_item = Item(
            manufacturer="Superuser",
            model="Superuser\'s Item",
            part_or_unit=Item.UNIT,
            # "part_number" is blank since it's a unit
        )
        cls.technician_item = Item(
            manufacturer="Technician",
            model="Technician\'s Item",
            part_or_unit=Item.UNIT,
            # "part_number" is blank since it's a unit
        )
        cls.intern_item = Item(
            manufacturer="Intern",
            model="Intern\'s Item",
            part_or_unit=Item.UNIT,
            # "part_number" is blank since it's a unit
        )
        cls.viewer_item = Item(
            manufacturer="Viewer",
            model="Viewer\'s Item",
            part_or_unit=Item.UNIT,
            # "part_number" is blank since it's a unit
        )
        items = [cls.superuser_item, cls.technician_item, cls.intern_item, cls.viewer_item]
        Item.objects.bulk_create(items)
        
        cls.superuser_item_delete_url = reverse("inventory:item_confirm_delete", kwargs={"pk": cls.superuser_item.pk})
        cls.technician_item_delete_url = reverse("inventory:item_confirm_delete", kwargs={"pk": cls.technician_item.pk})
        cls.intern_item_delete_url = reverse("inventory:item_confirm_delete", kwargs={"pk": cls.intern_item.pk})
        cls.viewer_item_delete_url = reverse("inventory:item_confirm_delete", kwargs={"pk": cls.viewer_item.pk})

        cls.client = Client()        
        
    @tag('critical')
    def test_item_delete_view_access_control(self):
        """
        Verify that only superusers and technicians can access the delete view.
        """
        self.client.login(username="testsuperuser", password="hayes4800")
        response = self.client.get(self.superuser_item_delete_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        
        self.client.login(username="testtechnician", password="hayes4800")
        response = self.client.get(self.technician_item_delete_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        
        self.client.login(username="testintern", password="hayes4800")
        response = self.client.get(self.intern_item_delete_url)
        self.assertEqual(response.status_code, 403)
        self.client.logout()
        
        self.client.login(username="testviewer", password="hayes4800")
        response = self.client.get(self.viewer_item_delete_url)
        self.assertEqual(response.status_code, 403)
        self.client.logout()
        
    def test_item_delete_as_superuser(self):
        """
        Superusers can delete items from the database.
        """
        self.client.login(username="testsuperuser", password="hayes4800")
        
        # Make sure canceling the deletion works
        response = self.client.post(self.superuser_item_delete_url, {"Cancel": "Cancel"})
        self.assertEqual(response.status_code, 302, "Response did not redirect after successful cancellation.")
        self.assertTrue(Item.objects.filter(pk=self.superuser_item.pk).exists(), "The item doesn't exist in the database.")
        
        # Delete the item and check that it's no longer in the database
        response = self.client.post(self.superuser_item_delete_url, {"Confirm": "Confirm"})
        self.assertEqual(response.status_code, 302, "Response did not redirect after successful deletion.")
        self.assertFalse(Item.objects.filter(pk=self.superuser_item.pk).exists(), "The item still exists in the database.")
        
    def test_item_delete_as_technician(self):
        """
        Technicians can delete items from the database.
        """
        self.client.login(username="testtechnician", password="hayes4800")
        
        # Make sure canceling the deletion works
        response = self.client.post(self.technician_item_delete_url, {"Cancel": "Cancel"})
        self.assertEqual(response.status_code, 302, "Response did not redirect after successful cancellation.")
        self.assertTrue(Item.objects.filter(pk=self.technician_item.pk).exists(), "The item doesn't exist in the database.")
        
        # Delete the item and check that it's no longer in the database        
        response = self.client.post(self.superuser_item_delete_url, {"Confirm": "Confirm"})
        self.assertEqual(response.status_code, 302, "Response did not redirect after successful deletion.")
        self.assertFalse(Item.objects.filter(pk=self.superuser_item.pk).exists(), "The item still exists in the database.")

    def test_item_delete_as_intern(self):
        """
        Interns cannot delete items from the database.
        """
        # TODO: test_item_delete_as_intern
        
    def test_item_delete_as_viewer(self):
        """
        Viewers cannot delete items from the database.
        """
        # TODO: test_item_delete_as_viewer
    
    
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
        
        # Check for form errors
        if response.context and 'form' in response.context:
            self.assertFalse(response.context['form'].errors, f"Form errors: {response.context['form'].errors}")
        
        # Make sure the item was created successfully and redirects
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Item.objects.filter(part_number="1285578").exists(), "This item doesn't exist.")
        
        # Check Item History for record of creation        
        item = Item.objects.filter(part_number="1285578").first()
        item_history = ItemHistory.objects.filter(item=item).first()
        
        self.assertIsNotNone(item_history, "The item's history doesn't exist.")
        self.assertEqual(item_history.action, "create", f"The action for this record should be 'create'. It is actually {item_history.action}.")
        self.assertEqual(item_history.user, self.user, f"The user responsible for the creation should be 'testuser'. It is actually {item_history.user}.")
        
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
        
    def test_item_history_view_record_of_use(self):
        """
        The ItemHistory view shows the record of an item being used by a user.
        """
        # TODO: test_item_history_view_record_of_use
        # User logs in
        login = self.client.login(username="testuser", password="password")
        self.assertTrue(login, "Login failed.")
        
        # Make sure the item from `setUpTestData` exists
        # self.assertTrue(Item.objects.filter(part_number="1285578").exists(), "This item doesn't exist.") 




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
        # [ ]: Create one user for each group
        
    
    


###################################################################################################
# Tests for the Views for the UsedItem Model ######################################################
###################################################################################################
class UsedItemViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # TODO: Set up test data
        # [ ]: Create one user for each group
        # [ ]: Create one item for updating
        
    
    def test_used_item_view_access_control(self):
        """
        
        """
        # TODO: test_used_item_view_access_control
        # [ ]: Superusers have access
        # [ ]: Technicians have access
        # [ ]: Interns don't have access
        # [ ]: Viewers don't have access


