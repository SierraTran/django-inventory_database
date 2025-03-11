from django.test import Client, TestCase 
from django.urls import reverse
import time_machine
import datetime

from django.contrib.auth.models import Group
from authentication.models import User
from inventory.models import Item, ItemHistory


# Create your tests here.
class ItemViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up
        """
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
        
        
class ItemDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up
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
        cls.viewer_group = Group.objects.create(name="Viewer")
        cls.intern_group = Group.objects.create(name="Intern")
        cls.technician_group = Group.objects.create(name="Technician")
        cls.superuser_group = Group.objects.create(name="Superuser")

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
        
        