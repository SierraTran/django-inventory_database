"""
This module defines test cases for testing the views of the inventory app.
"""

import datetime
from unittest.mock import patch
from decimal import Decimal
from django.test import Client, RequestFactory, TestCase, tag
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User, Group
from freezegun import freeze_time
from inventory.models import Item, ItemHistory, ItemRequest, UsedItem
from inventory.views import (
    ItemHistoryView,
    ItemRequestView,
    ItemView,
    UsedItemView,
)


###################################################################################################
# Tests for the Views for the Item Model ##########################################################
###################################################################################################
class ItemViewTests(TestCase):
    """
    Tests for ItemView
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up initial data.
        """
        items = [
            Item(
                manufacturer="Fluke", model="Dials", part_or_unit=Item.UNIT, quantity=7
            ),
            Item(
                manufacturer="Fluke",
                model="45",
                part_or_unit=Item.PART,
                part_number="814137 Rev 2",
                quantity=1,
            ),
            Item(
                manufacturer="Amprobe",
                model="Bodys",
                part_or_unit=Item.PART,
                part_number="ACDC-100 TRMS",
                quantity=2,
            ),
            Item(
                manufacturer="Fluke",
                model="45",
                part_or_unit=Item.PART,
                part_number="814137 Rev 102",
                quantity=1,
            ),
            Item(
                manufacturer="Chroma",
                part_or_unit=Item.PART,
                part_number="8-16500016",
                description="16502 Board",
                quantity=4,
                unit_price=341.40,
            ),
            Item(
                manufacturer="HP",
                model="Handles",
                part_or_unit=Item.PART,
                part_number="E3623A",
                quantity=2,
            ),
        ]
        Item.objects.bulk_create(items)
        cls.items_list_url = reverse("inventory:items")

        cls.technician_group = Group.objects.get(name="Technician")
        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.user.groups.add(cls.technician_group)

        cls.client = Client()
        cls.factory = RequestFactory()

    def test_get_queryset(self):
        """
        Test that the get_queryset function is working correctly
        """
        request = self.factory.get(self.items_list_url)
        view = ItemView()
        view.request = request
        queryset = Item.objects.all().order_by(
            "manufacturer", "model", "part_or_unit", "part_number", "quantity"
        )

        expected_ordered_items = [
            ("Amprobe", "Bodys", Item.PART, "ACDC-100 TRMS", 2),
            ("Chroma", "N/A", Item.PART, "8-16500016", 4),
            ("Fluke", "45", Item.PART, "814137 Rev 102", 1),
            ("Fluke", "45", Item.PART, "814137 Rev 2", 1),
            ("Fluke", "Dials", Item.UNIT, "", 7),
            ("HP", "Handles", Item.PART, "E3623A", 2),
        ]
        actual_ordered_items = list(
            queryset.values_list(
                "manufacturer", "model", "part_or_unit", "part_number", "quantity"
            )
        )

        self.assertEqual(queryset.count(), 6)
        self.assertEqual(actual_ordered_items, expected_ordered_items)

    def test_item_view_get_unauthenticated(self):
        """
        The ItemView redirects to the login page if the user is unauthenticated.
        """
        response = self.client.get(self.items_list_url, follow=True)

        # Make sure the followed response finds the page and uses the right template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_item_view_get_authenticated(self):
        """
        The ItemView displays all items in the database for authenticated users.
        """
        self.client.login(username="testuser", password="password")
        response = self.client.get(self.items_list_url)

        self.assertEqual(
            response.status_code, 200, "Authenticated user should get a 200 response."
        )
        self.assertTemplateUsed(
            response, "items.html", "ItemView should use the correct template."
        )

        expected_items = Item.objects.all().order_by(
            "manufacturer", "model", "part_number"
        )
        actual_items = response.context["items_list"]

        # Assert that all items in the database are displayed and in the correct order
        self.assertEqual(
            len(actual_items),
            Item.objects.count(),
            "The number of items in the context should match the database count.",
        )
        for i in range(0, len(actual_items)):
            self.assertEqual(list(actual_items)[i], list(expected_items)[i])


class ItemDetailViewTests(TestCase):
    """
    Tests for ItemDetailView
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up initial data.
        """
        cls.item = Item.objects.create(
            manufacturer="HP",
            model="Front panel",
            part_or_unit=Item.PART,
            part_number="8592E",
            description="Part for front panel",
            location="Shelf A2",
            quantity=3,
            unit_price=0.75,
        )

        # Get necessary groups
        cls.viewer_group = Group.objects.get(name="Viewer")
        cls.intern_group = Group.objects.get(name="Intern")
        cls.technician_group = Group.objects.get(name="Technician")
        cls.superuser_group = Group.objects.get(name="Superuser")

        # Create users and assign them to groups
        cls.viewer = User.objects.create_user(
            username="testviewer", password="password"
        )
        cls.viewer.groups.add(cls.viewer_group)

        cls.intern = User.objects.create_user(
            username="testintern", password="password"
        )
        cls.intern.groups.add(cls.intern_group)

        cls.technician = User.objects.create_user(
            username="testtechnician", password="password"
        )
        cls.technician.groups.add(cls.technician_group)

        cls.superuser = User.objects.create_superuser(
            username="testsuperuser", password="password"
        )
        cls.superuser.groups.add(cls.superuser_group)

        cls.client = Client()
        cls.item_detail_url_valid = reverse(
            "inventory:item_detail", kwargs={"pk": cls.item.pk}
        )

    def test_item_detail_get_unauthenticated(self):
        """
        The ItemDetailView redirects to the login page if the user is unauthenticated.
        """
        response = self.client.get(self.item_detail_url_valid, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_item_detail_get_viewer(self):
        """
        The ItemDetailView renders the detail page for the specific item with buttons for Viewers.
        """
        self.client.login(username="testviewer", password="password")
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
        self.assertNotContains(
            response, '<button type="button" class="delete" id="delete"'
        )

    def test_item_detail_get_intern(self):
        """
        The ItemDetailView renders the detail page for the specific item with buttons for Interns.
        """
        self.client.login(username="testintern", password="password")
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
        self.assertNotContains(
            response, '<button type="button" class="delete" id="delete"'
        )

    def test_item_detail_get_technician(self):
        """
        The ItemDetailView renders the detail page for the specific item with buttons for
        Technicians.
        """
        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.item_detail_url_valid, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "item_detail.html")

        # Technician has back, history, update, use, and request more buttons
        self.assertContains(response, '<button type="button" id="back"')
        self.assertContains(response, '<button type="button" id="history"')
        self.assertContains(response, '<button type="button" id="update"')
        self.assertContains(response, '<button type="button" id="use"')
        self.assertContains(response, '<button type="button" id="request-more"')
        self.assertContains(
            response, '<button type="button" class="delete" id="delete"'
        )

        # Technician doesn't have an order more button
        self.assertNotContains(response, '<button type="button" id="order-more"')

    def test_item_detail_get_superuser(self):
        """
        The ItemDetailView renders the detail page for the specific item with buttons for
        Superusers.
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.item_detail_url_valid, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "item_detail.html")

        # Superuser has back, history, update, use, order more, and delete buttons
        self.assertContains(response, '<button type="button" id="back"')
        self.assertContains(response, '<button type="button" id="history"')
        self.assertContains(response, '<button type="button" id="update"')
        self.assertContains(response, '<button type="button" id="use"')
        self.assertContains(response, '<button type="button" id="order-more"')
        self.assertContains(
            response, '<button type="button" class="delete" id="delete"'
        )

        # Superuser doesn't have a request more button
        self.assertNotContains(response, '<button type="button" id="request-more"')


class ItemCreateViewTests(TestCase):
    """
    Tests for ItemCreateView
    """

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
        cls.superuser = User.objects.create_superuser(
            username="testsuperuser", password="password"
        )
        cls.superuser.groups.add(cls.superuser_group)

        cls.technician = User.objects.create_user(
            username="testtechnician", password="password"
        )
        cls.technician.groups.add(cls.technician_group)

        cls.intern = User.objects.create_user(
            username="testintern", password="password"
        )
        cls.intern.groups.add(cls.intern_group)

        cls.viewer = User.objects.create_user(
            username="testviewer", password="password"
        )
        cls.viewer.groups.add(cls.viewer_group)

        # Get the URLs of the item create views
        cls.item_create_superuser_url = reverse("inventory:item_create_form_superuser")
        cls.item_create_technician_url = reverse(
            "inventory:item_create_form_technician"
        )

        cls.client = Client()

    @tag("critical")
    def test_item_create_superuser_view_access_control(self):
        """
        Verify that only superusers can access the superuser item creation view.
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.item_create_superuser_url)
        self.assertEqual(
            response.status_code, 200, "Superuser failed to access their own view."
        )
        self.assertTemplateUsed(response, "item_create_form.html")
        self.client.logout()

        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.item_create_superuser_url)
        self.assertEqual(
            response.status_code,
            403,
            "Technician unexpectedly gained access to superuser view.",
        )
        self.assertTemplateUsed(response, "403.html")
        self.client.logout()

        self.client.login(username="testintern", password="password")
        response = self.client.get(self.item_create_superuser_url)
        self.assertEqual(
            response.status_code,
            403,
            "Intern unexpectedly gained access to superuser view.",
        )
        self.assertTemplateUsed(response, "403.html")
        self.client.logout()

        self.client.login(username="testviewer", password="password")
        response = self.client.get(self.item_create_superuser_url)
        self.assertEqual(
            response.status_code,
            403,
            "Viewer unexpectedly gained access to superuser view.",
        )
        self.assertTemplateUsed(response, "403.html")
        self.client.logout()

    @tag("critical")
    def test_item_create_technician_view_access_control(self):
        """
        Verify that only technicians can access the technician item creation view.
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.item_create_technician_url)
        self.assertEqual(
            response.status_code,
            403,
            "Superuser unexpectedly gained access to technician view.",
        )
        self.assertTemplateUsed(response, "403.html")
        self.client.logout()

        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.item_create_technician_url)
        self.assertEqual(
            response.status_code, 200, "Technician failed to access their own view."
        )
        self.assertTemplateUsed(response, "item_create_form.html")
        self.client.logout()

        self.client.login(username="testintern", password="password")
        response = self.client.get(self.item_create_technician_url)
        self.assertEqual(
            response.status_code,
            403,
            "Intern unexpectedly gained access to technician view.",
        )
        self.assertTemplateUsed(response, "403.html")
        self.client.logout()

        self.client.login(username="testviewer", password="password")
        response = self.client.get(self.item_create_technician_url)
        self.assertEqual(
            response.status_code,
            403,
            "Viewer unexpectedly gained access to technician view.",
        )
        self.assertTemplateUsed(response, "403.html")
        self.client.logout()

    def test_item_create_as_superuser_with_superuser_view(self):
        """
        Make sure superusers can create items with only their own dedicated create view.
        """
        # Superuser logins in
        login = self.client.login(username="testsuperuser", password="password")
        self.assertTrue(login, "Login failed.")

        # Superuser creates an item in their dedicated view
        response = self.client.post(
            reverse("inventory:item_create_form_superuser"),
            {
                "manufacturer": "Superuser",
                "model": "Superuser's Item",
                "part_or_unit": Item.UNIT,
                # "part_number" is blank since it's a unit
                "description": "Item created by the Superuser",
                "location": "N/A",
                "quantity": 1,
                "min_quantity": 0,
                "unit_price": 0.01,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # Make sure the item was created successfully and redirects
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Item.objects.filter(model="Superuser's Item").exists(),
            "This item doesn't exist.",
        )

    def test_item_create_as_superuser_with_technician_view(self):
        """
        Superusers cannot create items with the technician view
        """
        login = self.client.login(username="testsuperuser", password="password")
        self.assertTrue(login, "Login failed.")

        response = self.client.post(
            self.item_create_technician_url,
            {
                "manufacturer": "Superuser",
                "model": "Superuser's Item",
                "part_or_unit": Item.UNIT,
                # "part_number" is blank since it's a unit
                "description": "Item created by the Superuser",
                "location": "N/A",
                "quantity": 1,
                # Technicians cannot set the min_quantity
                "unit_price": 0.01,
            },
        )

        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        self.assertFalse(
            Item.objects.filter(model="Superuser's Item").exists(),
            "This item does exist.",
        )

    def test_item_create_as_technician_with_superuser_view(self):
        """
        Technicians cannot create items with the superuser view
        """
        login = self.client.login(username="testtechnician", password="password")
        self.assertTrue(login, "Login failed.")

        response = self.client.post(
            reverse("inventory:item_create_form_superuser"),
            {
                "manufacturer": "Technician",
                "model": "Technician's Item",
                "part_or_unit": Item.UNIT,
                # "part_number" is blank since it's a unit
                "description": "Item created by the Technician",
                "location": "N/A",
                "quantity": 1,
                "min_quantity": 0,
                "unit_price": 0.01,
            },
        )

        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        self.assertFalse(
            Item.objects.filter(model="Technician's Item").exists(),
            "This item does exist.",
        )

    def test_item_create_as_technician_with_technician_view(self):
        """
        Make sure technicians can create items with only their own dedicated create view.
        """
        login = self.client.login(username="testtechnician", password="password")
        self.assertTrue(login, "Login failed.")

        # Technician creates an item in their dedicated view
        response = self.client.post(
            self.item_create_technician_url,
            {
                "manufacturer": "Technician",
                "model": "Technician's Item",
                "part_or_unit": Item.UNIT,
                # "part_number" is blank since it's a unit
                "description": "Item created by the Technician",
                "location": "N/A",
                "quantity": 1,
                # Technicians cannot set the min_quantity
                "unit_price": 0.01,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # Make sure the item was created successfully and redirects
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Item.objects.filter(model="Technician's Item").exists(),
            "This item doesn't exist.",
        )

    def test_item_create_as_intern_with_superuser_view(self):
        """
        Make sure interns can't create items.
        """
        login = self.client.login(username="testintern", password="password")
        self.assertTrue(login, "Login failed.")

        # Attempt to create an item with the superuser's view
        response = self.client.post(
            reverse("inventory:item_create_form_superuser"),
            {
                "manufacturer": "Intern",
                "model": "Intern's Item",
                "part_or_unit": Item.UNIT,
                # "part_number" is blank since it's a unit
                "description": "Item created by the Intern",
                "location": "N/A",
                "quantity": 1,
                "min_quantity": 0,
                "unit_price": 0.01,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # The item shouldn't exist in the database
        self.assertFalse(
            Item.objects.filter(model="Intern's Item").exists(), "This item does exist."
        )

    def test_item_create_as_intern_with_technician_view(self):
        """
        Make sure interns can't create items.
        """
        login = self.client.login(username="testintern", password="password")
        self.assertTrue(login, "Login failed.")

        # Attempt to create an item with the technician's view
        response = self.client.post(
            reverse("inventory:item_create_form_technician"),
            {
                "manufacturer": "Intern",
                "model": "Intern's Item",
                "part_or_unit": Item.UNIT,
                # "part_number" is blank since it's a unit
                "description": "Item created by the Intern",
                "location": "N/A",
                "quantity": 1,
                # Technicians cannot set the min_quantity
                "unit_price": 0.01,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # The item shouldn't exist in the database
        self.assertFalse(
            Item.objects.filter(model="Intern's Item").exists(), "This item does exist."
        )

    def test_item_create_as_viewer_with_superuser_view(self):
        """
        Make sure viewers can't create items with the superuser view.
        """
        login = self.client.login(username="testviewer", password="password")
        self.assertTrue(login, "Login failed.")

        # Attempt to create an item with the superuser's view
        response = self.client.post(
            reverse("inventory:item_create_form_superuser"),
            {
                "manufacturer": "Viewer",
                "model": "Viewer's Item",
                "part_or_unit": Item.UNIT,
                # "part_number" is blank since it's a unit
                "description": "Item created by the Intern",
                "location": "N/A",
                "quantity": 1,
                "min_quantity": 0,
                "unit_price": 0.01,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # The item shouldn't exist in the database
        self.assertFalse(
            Item.objects.filter(model="Viewer's Item").exists(), "This item does exist."
        )

    def test_item_create_as_viewer_with_technician_view(self):
        """
        Make sure viewers can't create items with the technician view.
        """
        login = self.client.login(username="testviewer", password="password")
        self.assertTrue(login, "Login failed.")

        # Attempt to create an item with the technician's view
        response = self.client.post(
            reverse("inventory:item_create_form_technician"),
            {
                "manufacturer": "Viewer",
                "model": "Viewer's Item",
                "part_or_unit": Item.UNIT,
                # "part_number" is blank since it's a unit
                "description": "Item created by the Intern",
                "location": "N/A",
                "quantity": 1,
                # Technicians cannot set the min_quantity
                "unit_price": 0.01,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # The item shouldn't exist in the database
        self.assertFalse(
            Item.objects.filter(model="Viewer's Item").exists(), "This item does exist."
        )


class ItemUpdateViewTests(TestCase):
    """
    Tests for ItemUpdateView
    """

    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # Create item to be updated
        cls.item = Item.objects.create(
            manufacturer="HP",
            model="Dual mixer",
            part_or_unit=Item.UNIT,
            # No part number since it's a unit
            # No description available, make blank
            # No location, set to default
            quantity=4,
            # No minimum quantity, set to default
            # No unit price, set to default
        )

        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.technician_group = Group.objects.get(name="Technician")
        cls.intern_group = Group.objects.get(name="Intern")
        cls.viewer_group = Group.objects.get(name="Viewer")

        # Create users and assign them to groups
        cls.superuser = User.objects.create_superuser(
            username="testsuperuser", password="password"
        )
        cls.superuser.groups.add(cls.superuser_group)
        cls.technician = User.objects.create_user(
            username="testtechnician", password="password"
        )
        cls.technician.groups.add(cls.technician_group)
        cls.intern = User.objects.create_user(
            username="testintern", password="password"
        )
        cls.intern.groups.add(cls.intern_group)
        cls.viewer = User.objects.create_user(
            username="testviewer", password="password"
        )
        cls.viewer.groups.add(cls.viewer_group)

        # Get the URLs of the item update views
        cls.item_update_superuser_url = reverse(
            "inventory:item_update_form_superuser", kwargs={"pk": cls.item.pk}
        )
        cls.item_update_technician_url = reverse(
            "inventory:item_update_form_technician", kwargs={"pk": cls.item.pk}
        )
        cls.item_update_intern_url = reverse(
            "inventory:item_update_form_intern", kwargs={"pk": cls.item.pk}
        )

        cls.factory = RequestFactory()
        cls.client = Client()
        # cls.view = ItemUpdateSuperuserView()

    @tag("critical")
    def test_item_update_superuser_view_access_control(self):
        """
        Only superusers have access to the superuser-only item update view
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.item_update_superuser_url)
        self.assertEqual(
            response.status_code, 200, "Superuser failed to access their own view."
        )
        self.client.logout()

        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.item_update_superuser_url)
        self.assertEqual(
            response.status_code,
            403,
            "Technician unexpectedly gained access to superuser view.",
        )
        self.client.logout()

        self.client.login(username="testintern", password="password")
        response = self.client.get(self.item_update_superuser_url)
        self.assertEqual(
            response.status_code,
            403,
            "Intern unexpectedly gained access to superuser view.",
        )
        self.client.logout()

        self.client.login(username="testviewer", password="password")
        response = self.client.get(self.item_update_superuser_url)
        self.assertEqual(
            response.status_code,
            403,
            "Viewer unexpectedly gained access to superuser view.",
        )
        self.client.logout()

    @tag("critical")
    def test_item_update_technician_view_access_control(self):
        """
        Only technicians have access to the technician-only item update view
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.item_update_technician_url)
        self.assertEqual(
            response.status_code,
            403,
            "Superuser unexpectedly gained access to technician view.",
        )
        self.client.logout()

        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.item_update_technician_url)
        self.assertEqual(
            response.status_code, 200, "Technician failed to access their own view."
        )
        self.client.logout()

        self.client.login(username="testintern", password="password")
        response = self.client.get(self.item_update_technician_url)
        self.assertEqual(
            response.status_code,
            403,
            "Intern unexpectedly gained access to technician view.",
        )
        self.client.logout()

        self.client.login(username="testviewer", password="password")
        response = self.client.get(self.item_update_technician_url)
        self.assertEqual(
            response.status_code,
            403,
            "Viewer unexpectedly gained access to technician view.",
        )
        self.client.logout()

    @tag("critical")
    def test_item_update_intern_view_access_control(self):
        """
        Only interns have access to the intern-only item update view
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.item_update_intern_url)
        self.assertEqual(
            response.status_code,
            403,
            "Superuser unexpectedly gained access to intern view.",
        )
        self.client.logout()

        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.item_update_intern_url)
        self.assertEqual(
            response.status_code,
            403,
            "Technician unexpectedly gained access to intern view.",
        )
        self.client.logout()

        self.client.login(username="testintern", password="password")
        response = self.client.get(self.item_update_intern_url)
        self.assertEqual(
            response.status_code, 200, "Intern failed to access their own view."
        )
        self.client.logout()

        self.client.login(username="testviewer", password="password")
        response = self.client.get(self.item_update_intern_url)
        self.assertEqual(
            response.status_code,
            403,
            "Viewer unexpectedly gained access to intern view.",
        )
        self.client.logout()

    def test_item_update_as_superuser_with_superuser_view(self):
        """
        Superusers can update all item details
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.post(
            self.item_update_superuser_url,
            {
                "manufacturer": "Superuser Manufacturer",
                "model": "Superuser Model",
                "part_or_unit": Item.PART,
                "part_number": "0A1B2C",
                "description": "This item has been updated by a superuser",
                "location": "Shelf",
                "quantity": 5,
                "min_quantity": 1,
                "unit_price": 0.10,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # Check for 302 status code for redirecting to the updated item
        self.assertEqual(
            response.status_code, 302, "Superuser failed to update the item."
        )

        # Refresh and check that the item has been updated
        self.item.refresh_from_db()
        self.assertEqual(
            self.item.manufacturer,
            "Superuser Manufacturer",
            "The manufacturer hasn't been updated.",
        )
        self.assertEqual(
            self.item.model, "Superuser Model", "The model hasn't been updated."
        )
        self.assertEqual(
            self.item.part_or_unit, Item.PART, "The part or unit hasn't been updated."
        )
        self.assertEqual(
            self.item.part_number, "0A1B2C", "The part number hasn't been updated."
        )
        self.assertEqual(
            self.item.description,
            "This item has been updated by a superuser",
            "The description hasn't been updated.",
        )
        self.assertEqual(
            self.item.location, "Shelf", "The location hasn't been updated."
        )
        self.assertEqual(self.item.quantity, 5, "The quantity hasn't been updated.")
        self.assertEqual(
            self.item.min_quantity, 1, "The minimum quantity hasn't been updated."
        )
        self.assertEqual(
            self.item.unit_price, Decimal("0.10"), "The unit price hasn't been updated."
        )

    def test_item_update_as_superuser_with_technician_view(self):
        """
        Superusers cannot update items using the technician view
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.post(
            self.item_update_technician_url,
            {
                "manufacturer": "Technician Manufacturer",
                "model": "Technician Model",
                "part_or_unit": Item.PART,
                "part_number": "0A1B2C",
                "description": "This item has been updated by a technician",
                "location": "Shelf",
                "quantity": 5,
                "unit_price": 0.10,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # Check for 403 status code
        self.assertEqual(
            response.status_code, 403, "Superuser succeeded in updating the item."
        )

        # Refresh and check that the item has not been updated
        self.item.refresh_from_db()
        self.assertEqual(
            self.item.manufacturer, "HP", "The manufacturer has been updated"
        )
        self.assertEqual(self.item.model, "Dual mixer", "The model has been updated")
        self.assertEqual(
            self.item.part_or_unit, Item.UNIT, "The part or unit has been updated"
        )
        self.assertEqual(self.item.part_number, "", "The part number has been updated")
        self.assertEqual(self.item.description, "", "The description has been updated")
        self.assertEqual(self.item.location, "N/A", "The location has been updated")
        self.assertEqual(self.item.quantity, 4, "The quantity has been updated")
        self.assertEqual(
            self.item.unit_price, Decimal("0.01"), "The unit price has been updated"
        )

    def test_item_update_as_superuser_with_intern_view(self):
        """
        Superusers cannot update items using the itnern view
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.post(
            self.item_update_intern_url,
            {
                "quantity": 5,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # Check for 403 status code
        self.assertEqual(
            response.status_code, 403, "Superuser succeeded in updating the item."
        )

        # Refresh and check that the item has not been updated
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 4, "The quantity has been updated.")

    def test_item_update_as_technician_with_superuser_view(self):
        """
        Technicians cannot update items using the superuser view
        """
        self.client.login(username="testtechnician", password="password")
        response = self.client.post(
            self.item_update_superuser_url,
            {
                "manufacturer": "Technician Manufacturer",
                "model": "Technician Model",
                "part_or_unit": Item.PART,
                "part_number": "0A1B2C",
                "description": "This item has been updated by a technician",
                "location": "Shelf",
                "quantity": 5,
                "min_quantity": 1,
                "unit_price": 0.10,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # Check for 403 status code
        self.assertEqual(
            response.status_code, 403, "Technician succeeded in updating the item."
        )

        # Refresh and check that the item has not been updated
        self.item.refresh_from_db()
        self.assertEqual(
            self.item.manufacturer, "HP", "The manufacturer has been updated"
        )
        self.assertEqual(self.item.model, "Dual mixer", "The model has been updated")
        self.assertEqual(
            self.item.part_or_unit, Item.UNIT, "The part or unit has been updated"
        )
        self.assertEqual(self.item.part_number, "", "The part number has been updated")
        self.assertEqual(self.item.description, "", "The description has been updated")
        self.assertEqual(self.item.location, "N/A", "The location has been updated")
        self.assertEqual(self.item.quantity, 4, "The quantity has been updated")
        self.assertEqual(
            self.item.min_quantity, 0, "The minimum quantity has been updated"
        )
        self.assertEqual(
            self.item.unit_price, Decimal("0.01"), "The unit price has been updated"
        )

    def test_item_update_as_technician_with_technician_view(self):
        """
        Technicians can update all item details except minimum quantity using the technician view
        """
        self.client.login(username="testtechnician", password="password")
        response = self.client.post(
            self.item_update_technician_url,
            {
                "manufacturer": "Technician Manufacturer",
                "model": "Technician Model",
                "part_or_unit": Item.PART,
                "part_number": "0A1B2C",
                "description": "This item has been updated by a technician",
                "location": "Shelf",
                "quantity": 5,
                "unit_price": 0.10,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # Check for 302 status code for redirecting to the updated item
        self.assertEqual(
            response.status_code, 302, "Technician failed to update the item."
        )

        # Refresh and check that the item has been updated
        self.item.refresh_from_db()
        self.assertEqual(
            self.item.manufacturer,
            "Technician Manufacturer",
            "The manufacturer hasn't been updated.",
        )
        self.assertEqual(
            self.item.model, "Technician Model", "The model hasn't been updated."
        )
        self.assertEqual(
            self.item.part_or_unit, Item.PART, "The part or unit hasn't been updated."
        )
        self.assertEqual(
            self.item.part_number, "0A1B2C", "The part number hasn't been updated."
        )
        self.assertEqual(
            self.item.description,
            "This item has been updated by a technician",
            "The description hasn't been updated.",
        )
        self.assertEqual(
            self.item.location, "Shelf", "The location hasn't been updated."
        )
        self.assertEqual(self.item.quantity, 5, "The quantity hasn't been updated.")
        self.assertEqual(
            self.item.unit_price, Decimal("0.10"), "The unit price hasn't been updated."
        )

    def test_item_update_as_technician_with_intern_view(self):
        """
        Technicians cannot update items using the intern view
        """
        self.client.login(username="testtechnician", password="password")
        response = self.client.post(
            self.item_update_intern_url,
            {
                "quantity": 5,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # Check for 403 status code
        self.assertEqual(
            response.status_code, 403, "Technician succeeded in updating the item."
        )

        # Refresh and check that the item has not been updated
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 4, "The quantity has been updated.")

    def test_item_update_as_intern_with_superuser_view(self):
        """
        Interns cannot update items using the superuser view
        """
        self.client.login(username="testintern", password="password")
        response = self.client.post(
            self.item_update_superuser_url,
            {
                "manufacturer": "Technician Manufacturer",
                "model": "Technician Model",
                "part_or_unit": Item.PART,
                "part_number": "0A1B2C",
                "description": "This item has been updated by a technician",
                "location": "Shelf",
                "quantity": 5,
                "min_quantity": 1,
                "unit_price": 0.10,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # Check for 403 status code
        self.assertEqual(
            response.status_code, 403, "Technician succeeded in updating the item."
        )

        # Refresh and check that the item has not been updated
        self.item.refresh_from_db()
        self.assertEqual(
            self.item.manufacturer, "HP", "The manufacturer has been updated"
        )
        self.assertEqual(self.item.model, "Dual mixer", "The model has been updated")
        self.assertEqual(
            self.item.part_or_unit, Item.UNIT, "The part or unit has been updated"
        )
        self.assertEqual(self.item.part_number, "", "The part number has been updated")
        self.assertEqual(self.item.description, "", "The description has been updated")
        self.assertEqual(self.item.location, "N/A", "The location has been updated")
        self.assertEqual(self.item.quantity, 4, "The quantity has been updated")
        self.assertEqual(
            self.item.min_quantity, 0, "The minimum quantity has been updated"
        )
        self.assertEqual(
            self.item.unit_price, Decimal("0.01"), "The unit price has been updated"
        )

    def test_item_update_as_intern_with_technician_view(self):
        """
        Interns cannot update items using the technician view
        """
        self.client.login(username="testintern", password="password")
        response = self.client.post(
            self.item_update_technician_url,
            {
                "manufacturer": "Technician Manufacturer",
                "model": "Technician Model",
                "part_or_unit": Item.PART,
                "part_number": "0A1B2C",
                "description": "This item has been updated by a technician",
                "location": "Shelf",
                "quantity": 5,
                "unit_price": 0.10,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # Check for 403 status code
        self.assertEqual(
            response.status_code, 403, "Superuser succeeded in updating the item."
        )

        # Refresh and check that the item has not been updated
        self.item.refresh_from_db()
        self.assertEqual(
            self.item.manufacturer, "HP", "The manufacturer has been updated"
        )
        self.assertEqual(self.item.model, "Dual mixer", "The model has been updated")
        self.assertEqual(
            self.item.part_or_unit, Item.UNIT, "The part or unit has been updated"
        )
        self.assertEqual(self.item.part_number, "", "The part number has been updated")
        self.assertEqual(self.item.description, "", "The description has been updated")
        self.assertEqual(self.item.location, "N/A", "The location has been updated")
        self.assertEqual(self.item.quantity, 4, "The quantity has been updated")
        self.assertEqual(
            self.item.unit_price, Decimal("0.01"), "The unit price has been updated"
        )

    def test_item_update_as_intern_with_intern_view(self):
        """
        Interns can use the intern view and update an item's quantity
        """
        self.client.login(username="testintern", password="password")
        response = self.client.post(
            self.item_update_intern_url,
            {
                "quantity": 5,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # Check for 302 status code for redirecting to the updated item
        self.assertEqual(response.status_code, 302, "Intern failed to update the item.")

        # Refresh and check that the item has been updated
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 5, "The quantity hasn't been updated.")

    def test_item_update_as_viewer_with_superuser_view(self):
        """
        Viewers cannot update items using the superuser view
        """
        self.client.login(username="testviewer", password="password")
        response = self.client.post(
            self.item_update_superuser_url,
            {
                "manufacturer": "Technician Manufacturer",
                "model": "Technician Model",
                "part_or_unit": Item.PART,
                "part_number": "0A1B2C",
                "description": "This item has been updated by a technician",
                "location": "Shelf",
                "quantity": 5,
                "min_quantity": 1,
                "unit_price": 0.10,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # Check for 403 status code
        self.assertEqual(
            response.status_code, 403, "Technician succeeded in updating the item."
        )

        # Refresh and check that the item has not been updated
        self.item.refresh_from_db()
        self.assertEqual(
            self.item.manufacturer, "HP", "The manufacturer has been updated"
        )
        self.assertEqual(self.item.model, "Dual mixer", "The model has been updated")
        self.assertEqual(
            self.item.part_or_unit, Item.UNIT, "The part or unit has been updated"
        )
        self.assertEqual(self.item.part_number, "", "The part number has been updated")
        self.assertEqual(self.item.description, "", "The description has been updated")
        self.assertEqual(self.item.location, "N/A", "The location has been updated")
        self.assertEqual(self.item.quantity, 4, "The quantity has been updated")
        self.assertEqual(
            self.item.min_quantity, 0, "The minimum quantity has been updated"
        )
        self.assertEqual(
            self.item.unit_price, Decimal("0.01"), "The unit price has been updated"
        )

    def test_item_update_as_viewer_with_technician_view(self):
        """
        Viewers cannot update items using the technician view
        """
        self.client.login(username="testviewer", password="password")
        response = self.client.post(
            self.item_update_technician_url,
            {
                "manufacturer": "Technician Manufacturer",
                "model": "Technician Model",
                "part_or_unit": Item.PART,
                "part_number": "0A1B2C",
                "description": "This item has been updated by a technician",
                "location": "Shelf",
                "quantity": 5,
                "unit_price": 0.10,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # Check for 403 status code
        self.assertEqual(
            response.status_code, 403, "Superuser succeeded in updating the item."
        )

        # Refresh and check that the item has not been updated
        self.item.refresh_from_db()
        self.assertEqual(
            self.item.manufacturer, "HP", "The manufacturer has been updated"
        )
        self.assertEqual(self.item.model, "Dual mixer", "The model has been updated")
        self.assertEqual(
            self.item.part_or_unit, Item.UNIT, "The part or unit has been updated"
        )
        self.assertEqual(self.item.part_number, "", "The part number has been updated")
        self.assertEqual(self.item.description, "", "The description has been updated")
        self.assertEqual(self.item.location, "N/A", "The location has been updated")
        self.assertEqual(self.item.quantity, 4, "The quantity has been updated")
        self.assertEqual(
            self.item.unit_price, Decimal("0.01"), "The unit price has been updated"
        )

    def test_item_update_as_viewer_with_intern_view(self):
        """
        Viewers cannot update items using the intern view
        """
        self.client.login(username="testviewer", password="password")
        response = self.client.post(
            self.item_update_intern_url,
            {
                "quantity": 5,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # Check for 403 status code
        self.assertEqual(
            response.status_code, 403, "Technician succeeded in updating the item."
        )

        # Refresh and check that the item has not been updated
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 4, "The quantity has been updated.")

    @patch("inventory.models.Item.save")  # Mock the save method
    def test_save_adds_superuser_in_view(self, mock_save):
        """
        Test that the save method for ItemUpdateSuperuserView saves the superuser
        """
        self.client.login(username="testsuperuser", password="password")

        response = self.client.post(
            self.item_update_superuser_url,
            {
                "manufacturer": "Updated Manufacturer",
                "model": "Updated Model",
                "part_or_unit": Item.PART,
                "part_number": "12345",
                "description": "Updated description",
                "location": "Updated location",
                "quantity": 10,
                "min_quantity": 2,
                "unit_price": 1.50,
            },
        )

        mock_save.assert_called_once()
        args, kwargs = mock_save.call_args
        self.assertIn("user", kwargs)
        self.assertEqual(kwargs["user"], self.superuser)
        self.assertEqual(response.status_code, 302)


class ItemDeleteViewTests(TestCase):
    """
    Tests for ItemDeleteView
    """

    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # Get the user groups
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.technician_group = Group.objects.get(name="Technician")
        cls.intern_group = Group.objects.get(name="Intern")
        cls.viewer_group = Group.objects.get(name="Viewer")

        # Create users and assign them to the groups
        cls.superuser = User.objects.create_superuser(
            username="testsuperuser", password="password"
        )
        cls.superuser.groups.add(cls.superuser_group)

        cls.technician = User.objects.create_user(
            username="testtechnician", password="password"
        )
        cls.technician.groups.add(cls.technician_group)

        cls.intern = User.objects.create_user(
            username="testintern", password="password"
        )
        cls.intern.groups.add(cls.intern_group)

        cls.viewer = User.objects.create_user(
            username="testviewer", password="password"
        )
        cls.viewer.groups.add(cls.viewer_group)

        # Create an item for each user to attempt to delete
        cls.item = Item.objects.create(
            manufacturer="Chroma",
            # model : "N/A"
            part_or_unit=Item.PART,
            part_number="G53 003700",
            description="Fan part",
            # location : "N/A"
            quantity=50,
            # min_quantity : 0
            unit_price=0.80,
        )

        # Get the delete URLs for the items
        cls.item_delete_url = reverse(
            "inventory:item_confirm_delete", kwargs={"pk": cls.item.pk}
        )

        cls.client = Client()

    @tag("critical")
    def test_item_delete_view_access_control(self):
        """
        Verify that only superusers and technicians can access the delete view.
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.item_delete_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.item_delete_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        self.client.login(username="testintern", password="password")
        response = self.client.get(self.item_delete_url)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        self.client.login(username="testviewer", password="password")
        response = self.client.get(self.item_delete_url)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_item_delete_as_superuser(self):
        """
        Superusers can delete items from the database.
        """
        self.client.login(username="testsuperuser", password="password")

        # Make sure canceling the deletion works
        response = self.client.post(self.item_delete_url, {"Cancel": "Cancel"})
        self.assertEqual(
            response.status_code,
            302,
            "Response did not redirect after successful cancellation.",
        )
        self.assertTrue(
            Item.objects.filter(pk=self.item.pk).exists(),
            "The item doesn't exist in the database.",
        )

        # Delete the item and check that it's no longer in the database
        response = self.client.post(self.item_delete_url, {"Confirm": "Confirm"})
        self.assertEqual(
            response.status_code,
            302,
            "Response did not redirect after successful deletion.",
        )
        self.assertFalse(
            Item.objects.filter(pk=self.item.pk).exists(),
            "The item still exists in the database.",
        )

    def test_item_delete_as_technician(self):
        """
        Technicians can delete items from the database.
        """
        self.client.login(username="testtechnician", password="password")

        # Make sure canceling the deletion works
        response = self.client.post(self.item_delete_url, {"Cancel": "Cancel"})
        self.assertEqual(
            response.status_code,
            302,
            "Response did not redirect after successful cancellation.",
        )
        self.assertTrue(
            Item.objects.filter(pk=self.item.pk).exists(),
            "The item doesn't exist in the database.",
        )

        # Delete the item and check that it's no longer in the database
        response = self.client.post(self.item_delete_url, {"Confirm": "Confirm"})
        self.assertEqual(
            response.status_code,
            302,
            "Response did not redirect after successful deletion.",
        )
        self.assertFalse(
            Item.objects.filter(pk=self.item.pk).exists(),
            "The item still exists in the database.",
        )

    def test_item_delete_as_intern(self):
        """
        Interns cannot delete items from the database.
        """
        self.client.login(username="testintern", password="password")

        # Make sure canceling the deletion doesn't work due to forbidden access (403)
        response = self.client.post(self.item_delete_url, {"Cancel": "Cancel"})
        self.assertEqual(
            response.status_code, 403, "Intern was able to cancel deletion."
        )
        # Item should still be in the database
        self.assertTrue(
            Item.objects.filter(pk=self.item.pk).exists(),
            "The item doesn't exist in the database.",
        )

        # Deleting the item shoudn't work and instead result in a 403 status code
        response = self.client.post(self.item_delete_url, {"Confirm": "Confirm"})
        self.assertEqual(
            response.status_code, 403, "Intern was able to delete the item."
        )
        # Item should still be in the database
        self.assertTrue(
            Item.objects.filter(pk=self.item.pk).exists(),
            "The item doesn't exists in the database.",
        )

    def test_item_delete_as_viewer(self):
        """
        Viewers cannot delete items from the database.
        """
        self.client.login(username="testviewer", password="password")

        # Make sure canceling the deletion doesn't work due to forbidden access (403)
        response = self.client.post(self.item_delete_url, {"Cancel": "Cancel"})
        self.assertEqual(
            response.status_code, 403, "Viewer was able to cancel deletion."
        )
        # Item should still be in the database
        self.assertTrue(
            Item.objects.filter(pk=self.item.pk).exists(),
            "The item doesn't exist in the database.",
        )

        # Deleting the item shoudn't work and instead result in a 403 status code
        response = self.client.post(self.item_delete_url, {"Confirm": "Confirm"})
        self.assertEqual(
            response.status_code, 403, "Viewer was able to delete the item."
        )
        # Item should still be in the database
        self.assertTrue(
            Item.objects.filter(pk=self.item.pk).exists(),
            "The item doesn't exists in the database.",
        )


###################################################################################################
# Tests for the Views for the ItemHistory Model ###################################################
###################################################################################################
class ItemHistoryViewTests(TestCase):
    """
    Tests for ItemHistoryView
    """

    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # Assume all users have access to Item History and the button to go to its page.

        cls.user = User.objects.create_user(username="testuser", password="password")
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.user.groups.add(cls.superuser_group)

        cls.item = Item.objects.create(
            manufacturer="Fluke",
            model="N/A",
            part_or_unit=Item.PART,
            part_number="1285578",
            description="Power supply connector",
            location="Closet",
            quantity=3,
            min_quantity=0,
            unit_price=11.33,
        )

        cls.item_update_url = reverse(
            "inventory:item_update_form_superuser", kwargs={"pk": cls.item.pk}
        )
        cls.item_history_url = reverse(
            "inventory:item_history", kwargs={"pk": cls.item.pk}
        )

        cls.client = Client()
        cls.factory = RequestFactory()

    def test_get_queryset(self):
        """
        Test the queryset for the item's history.
        """
        request = self.factory.get(self.item_history_url)
        view = ItemHistoryView()
        view.request = request
        view.kwargs = {"pk": self.item.pk}
        queryset = view.get_queryset()

        expected_history = [
            (
                self.item.pk,
                ItemHistory.ACTION_CHOICES[0][0],
                None,
                "Created and added to the database.",
            ),
        ]
        actual_history = list(queryset.values_list("item", "action", "user", "changes"))

        self.assertEqual(
            len(actual_history), 1, "The queryset should only contain one item."
        )
        self.assertEqual(
            actual_history,
            expected_history,
            "The queryset does not match the expected history.",
        )

    def test_get_context_data(self):
        """
        Test the context data for the view
        """
        # Simulate GET request
        request = self.factory.get(self.item_history_url)
        view = ItemHistoryView()
        view.request = request
        view.kwargs = {"pk": self.item.pk}

        # Set the object_list attribute by calling get_queryset
        view.object_list = view.get_queryset()

        # Call get_context_data
        context_data = view.get_context_data()

        self.assertIn(
            "item", context_data, "The context does not contain the 'item' key."
        )
        self.assertEqual(
            context_data["item"],
            self.item,
            "The 'item' in the context does not match the expected item",
        )

    def test_item_history_view_record_of_creation(self):
        """
        The ItemHistory view shows the record of an item's creation by a user.

        For records showing no user associated with the creation, see the
        `test_history_action_create` test function in tests_models.py.
        """
        # User logs in
        login = self.client.login(username="testuser", password="password")
        self.assertTrue(login, "Login failed.")

        # User creates an Item
        response = self.client.post(
            reverse("inventory:item_create_form_superuser"),
            {
                "manufacturer": "HP",
                "model": "Main board",
                "part_or_unit": Item.PART,
                "part_number": "0482D",
                "description": "",
                "location": "Closet",
                "quantity": 1,
                "min_quantity": 0,
                "unit_price": 2.00,
            },
        )

        # Check for form errors
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )

        # Make sure the item was created successfully and redirects
        self.assertEqual(response.status_code, 302, "User failed to create the item.")
        self.assertTrue(
            Item.objects.filter(part_number="0482D").exists(),
            "This item doesn't exist.",
        )

        # Check Item History for record of creation
        item = Item.objects.filter(part_number="0482D").first()
        item_history = ItemHistory.objects.filter(item=item).first()

        self.assertIsNotNone(item_history, "The item's history doesn't exist.")
        self.assertEqual(
            item_history.action,
            "create",
            f"The action for this record should be 'create'. It is actually {item_history.action}.",
        )
        self.assertEqual(
            item_history.user,
            self.user,
            f"The user responsible for the creation should be {self.user}. It is actually {item_history.user}.",
        )
        self.assertEqual(
            item_history.changes,
            "Created and added to the database.",
            "The changes field does not match the expected value.",
        )

        # TODO: Check that the item history view shows the complete history for the item

    def test_item_history_view_record_of_update(self):
        """
        The ItemHistory view shows the record of an item's update by a user
        """
        # TODO: test_item_history_view_record_of_update
        # [x]: User logs in
        # [ ]: User updates the existing item
        # [ ]: Check for form errors
        # [ ]: Make sure the item was updated successfully and redirects
        # [ ]: Refresh with `self.item.refresh_from_db()`
        # [ ]: Check that the item history view shows the complete history for the item
        login = self.client.login(username="testuser", password="password")
        self.assertTrue(login, "Login failed.")

    def test_item_history_view_record_of_use(self):
        """
        The ItemHistory view shows the record of an item being used by a user.
        """
        # TODO: test_item_history_view_record_of_use
        # [x]: User logs in
        login = self.client.login(username="testuser", password="password")
        self.assertTrue(login, "Login failed.")

        # Make sure the item from `setUpTestData` exists
        # [ ]: User uses the existing item
        # [ ]: Check for form errors
        # [ ]: Make sure the item was updated successfully and redirects
        # [ ]: Refresh with `self.item.refresh_from_db()`
        # [ ]: Check that the item history view shows the complete history for the item

###################################################################################################
# Tests for the Views for the ItemRequest Model ###################################################
###################################################################################################
class ItemRequestViewTests(TestCase):
    """
    Tests for ItemRequestView
    """

    # NOTE: Local date and time is set to January 3, 2025 at 1:00 PM for testing purposes
    aware_datetime = timezone.make_aware(datetime.datetime(2025, 1, 3, 13, 0, 0))

    @classmethod
    @freeze_time(aware_datetime)
    def setUpTestData(cls):
        """
        Setup
        """
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.technician_group = Group.objects.get(name="Technician")
        cls.intern_group = Group.objects.get(name="Intern")
        cls.viewer_group = Group.objects.get(name="Viewer")

        cls.superuser = User.objects.create_user(
            username="testsuperuser", password="password"
        )
        cls.superuser.groups.add(cls.superuser_group)
        cls.technician = User.objects.create_user(
            username="testtechnician", password="password"
        )
        cls.technician.groups.add(cls.technician_group)
        cls.intern = User.objects.create_user(
            username="testintern", password="password"
        )
        cls.intern.groups.add(cls.intern_group)
        cls.viewer = User.objects.create_user(
            username="testviewer", password="password"
        )
        cls.viewer.groups.add(cls.viewer_group)

        item_requests = [
            ItemRequest(
                manufacturer="Test MFG",
                model_part_num="First Model and Part Num",
                quantity_requested=1,
                # description left blank
                unit_price=0.01,
                requested_by=cls.technician,
                # timestamp automatically set
                # status automatically set to "Pending"
                # status_changed_by automatically set to None
            ),
            ItemRequest(
                manufacturer="Test MFG",
                model_part_num="Second Model and Part Num",
                quantity_requested=1,
                unit_price=0.01,
                requested_by=cls.technician,
            ),
            ItemRequest(
                manufacturer="Test MFG",
                model_part_num="Third Model and Part Num",
                quantity_requested=1,
                unit_price=0.01,
                requested_by=cls.technician,
            ),
            ItemRequest(
                manufacturer="Test MFG",
                model_part_num="Fourth Model and Part Num",
                quantity_requested=1,
                unit_price=0.01,
                requested_by=cls.technician,
            ),
        ]
        ItemRequest.objects.bulk_create(item_requests)

        cls.item_requests_url = reverse("inventory:item_requests")
        cls.client = Client()
        cls.factory = RequestFactory()

    @tag("critical")
    def test_item_request_view_access_control(self):
        """
        Test that only superusers and technicians can access the view
        """
        # Superuser access
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.item_requests_url)
        self.assertEqual(
            response.status_code,
            200,
            "Superuser failed to access the item requests view.",
        )
        self.client.logout()

        # Technician access
        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.item_requests_url)
        self.assertEqual(
            response.status_code,
            200,
            "Technician failed to access the item requests view.",
        )
        self.client.logout()

        # Intern forbidden
        self.client.login(username="testintern", password="password")
        response = self.client.get(self.item_requests_url)
        self.assertEqual(
            response.status_code,
            403,
            "Intern was able to access the item requests view.",
        )
        self.client.logout()

        # Viewer forbidden
        self.client.login(username="testviewer", password="password")
        response = self.client.get(self.item_requests_url)
        self.assertEqual(
            response.status_code,
            403,
            "Viewer was able to access the item requests view.",
        )
        self.client.logout()

    def test_get_queryset(self):
        """
        Test the queryset for the item requests.
        """
        request = self.factory.get(self.item_requests_url)
        view = ItemRequestView()
        view.request = request
        queryset = view.get_queryset()

        expected_ordered_item_requests = [
            ("Test MFG", "First Model and Part Num"),
            ("Test MFG", "Second Model and Part Num"),
            ("Test MFG", "Third Model and Part Num"),
            ("Test MFG", "Fourth Model and Part Num"),
        ]
        actual_ordered_item_requests = list(
            queryset.values_list("manufacturer", "model_part_num")
        )

        self.assertEqual(queryset.count(), 4)
        self.assertEqual(actual_ordered_item_requests, expected_ordered_item_requests)


class ItemRequestDetailViewTests(TestCase):
    """
    Tests for ItemRequestDetailView
    """

    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.technician_group = Group.objects.get(name="Technician")
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.intern_group = Group.objects.get(name="Intern")
        cls.viewer_group = Group.objects.get(name="Viewer")

        cls.superuser = User.objects.create_user(
            username="testsuperuser", password="password"
        )
        cls.superuser.groups.add(cls.superuser_group)
        cls.technician = User.objects.create_user(
            username="testtechnician", password="password"
        )
        cls.technician.groups.add(cls.technician_group)
        cls.intern = User.objects.create_user(
            username="testintern", password="password"
        )
        cls.intern.groups.add(cls.intern_group)
        cls.viewer = User.objects.create_user(
            username="testviewer", password="password"
        )
        cls.viewer.groups.add(cls.viewer_group)

        cls.item_request = ItemRequest.objects.create(
            manufacturer="Test MFG",
            model_part_num="First Model and Part Num",
            quantity_requested=1,
            unit_price=0.01,
            requested_by=cls.technician,
        )
        cls.item_request_detail_url = reverse(
            "inventory:item_request_detail", kwargs={"pk": cls.item_request.pk}
        )

        cls.client = Client()

    @tag("critical")
    def test_item_request_detail_view_access_control(self):
        """
        Test that only superusers and technicians can see item request details
        """
        # Superuser access
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.item_request_detail_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        # Technician access
        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.item_request_detail_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        # Intern forbidden
        self.client.login(username="testintern", password="password")
        response = self.client.get(self.item_request_detail_url)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # Viewer forbidden
        self.client.login(username="testviewer", password="password")
        response = self.client.get(self.item_request_detail_url)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_get_superuser(self):
        """
        Test that the view renders the correct template and the correct buttons for superusers.
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.item_request_detail_url)
        self.assertEqual(
            response.status_code,
            200,
            "Superuser failed to access the item request detail view.",
        )
        self.assertTemplateUsed(response, "item_request_detail.html")

        # Superuser has reject and accept buttons
        self.assertContains(response, '<button type="button" name="reject"')
        self.assertContains(response, '<button type="button" name="accept"')

        # Superuser doesn't have a delete button
        self.assertNotContains(response, '<button type="button" name="delete"')

    def test_get_technician_owner(self):
        """
        Test that the view renders the correct template and the correct buttons for the technician that made the item request.
        """
        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.item_request_detail_url)
        self.assertEqual(
            response.status_code,
            200,
            "Technician Owner failed to access the item request detail view.",
        )
        self.assertTemplateUsed(response, "item_request_detail.html")

        # Technician Owner has a delete button
        self.assertContains(response, '<button type="button" name="delete"')

        # Technician Owner doesn't have reject and accept buttons
        self.assertNotContains(response, '<button type="button" name="reject"')
        self.assertNotContains(response, '<button type="button" name="accept"')


class ItemRequestCreateViewTests(TestCase):
    """
    Tests for ItemRequestCreateView
    """

    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.technician_group = Group.objects.get(name="Technician")
        cls.technician = User.objects.create_user(
            username="testtechnician", password="password"
        )
        cls.technician.groups.add(cls.technician_group)
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.superuser = User.objects.create_user(
            username="testsuperuser", password="password"
        )
        cls.superuser.groups.add(cls.superuser_group)
        cls.intern_group = Group.objects.get(name="Intern")
        cls.intern = User.objects.create_user(
            username="testintern", password="password"
        )
        cls.intern.groups.add(cls.intern_group)
        cls.viewer_group = Group.objects.get(name="Viewer")
        cls.viewer = User.objects.create_user(
            username="testviewer", password="password"
        )
        cls.viewer.groups.add(cls.viewer_group)

        cls.item = Item.objects.create(
            manufacturer="Test MFG",
            model="Test Model",
            part_or_unit=Item.PART,
            part_number="Test Part Number",
            description="Test Description",
            location="Test Location",
            quantity=10,
            min_quantity=0,
            unit_price=0.10,
        )
        cls.item_request_form_url = reverse("inventory:item_request_form")
        cls.url_parameters = f"?item_id={cls.item.pk}&manufacturer={cls.item.manufacturer}&model_part_num={cls.item.model}&unit_price={cls.item.unit_price}&description={cls.item.description}"

        cls.client = Client()

    def test_item_request_create_view_access_control(self):
        """
        Test that only technicians can access the view.
        """
        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.item_request_form_url)
        self.assertEqual(
            response.status_code,
            200,
            "Technician failed to access the item request form view.",
        )

        self.client.logout()

        # Test that other users cannot access the view
        for user in ["testsuperuser", "testintern", "testviewer"]:
            self.client.login(username=user, password="password")
            response = self.client.get(self.item_request_form_url)
            self.assertEqual(
                response.status_code,
                403,
                f"{user} was able to access the item request form view.",
            )
            self.client.logout()

    def test_create_item_request_no_params(self):
        """
        Test that the item request is created successfully with no parameters.
        """
        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.item_request_form_url)
        self.assertEqual(response.status_code, 200, "Failed to access the view.")

        response = self.client.post(
            self.item_request_form_url,
            {
                "manufacturer": "Test MFG",
                "model_part_num": "Test Model Part Number",
                "quantity_requested": 2,
                # description will be blank
                "unit_price": 0.10,
            },
        )
        self.assertEqual(
            response.status_code, 302, "Failed to create the item request."
        )

        new_item_request = ItemRequest.objects.filter(pk=1)
        self.assertTrue(new_item_request.exists(), "The item request does not exist.")

    def test_create_item_request_with_params(self):
        """
        Test that the item request is created successfully with parameters.
        """
        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.item_request_form_url + self.url_parameters)
        self.assertEqual(response.status_code, 200, "Failed to access the view.")

        response = self.client.post(
            self.item_request_form_url + self.url_parameters,
            {"quantity_requested": 2, "unit_price": 0.10},
        )
        if response.context and "form" in response.context:
            self.assertFalse(
                response.context["form"].errors,
                f"Form errors: {response.context['form'].errors}",
            )
        self.assertEqual(
            response.status_code, 302, "Failed to create the item request."
        )

        new_item_request = ItemRequest.objects.filter(pk=1)
        self.assertTrue(new_item_request.exists(), "The item request does not exist.")


class ItemRequestAcceptViewTests(TestCase):
    """
    Tests for ItemRequestAcceptView
    """

    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.superuser = User.objects.create_superuser(
            username="testsuperuser", password="password"
        )
        cls.superuser.groups.add(cls.superuser_group)
        cls.technician_group = Group.objects.get(name="Technician")
        cls.technician = User.objects.create_user(
            username="testtechnician", password="password"
        )
        cls.technician.groups.add(cls.technician_group)
        cls.item_request = ItemRequest.objects.create(
            manufacturer="Test MFG",
            model_part_num="Accept Model",
            quantity_requested=1,
            unit_price=0.01,
            requested_by=cls.technician,
        )
        cls.accept_url = reverse(
            "inventory:item_request_confirm_accept", kwargs={"pk": cls.item_request.pk}
        )

    def test_get_object(self):
        """
        Test that the correct object is returned in the context
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.accept_url)
        self.assertEqual(response.context["object"], self.item_request)

    def test_get_context_data(self):
        """
        Test the context data for the view
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.accept_url)
        self.assertIn("object", response.context)
        self.assertEqual(response.context["object"], self.item_request)

    def test_post(self):
        """
        Test that the item request is accepted successfully.
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.post(self.accept_url, {"Confirm": "Confirm"})
        self.assertEqual(response.status_code, 302)
        self.item_request.refresh_from_db()
        self.assertEqual(self.item_request.status, "Accepted")

    def test_post_cancel(self):
        """
        Test that the item request is not accepted when canceling.
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.post(self.accept_url, {"Cancel": "Cancel"})
        self.assertEqual(response.status_code, 302)
        self.item_request.refresh_from_db()
        self.assertNotEqual(self.item_request.status, "Accepted")


class ItemRequestRejectViewTests(TestCase):
    """
    Tests for ItemRequestRejectView
    """

    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.superuser = User.objects.create_superuser(
            username="testsuperuser", password="password"
        )
        cls.superuser.groups.add(cls.superuser_group)
        cls.technician_group = Group.objects.get(name="Technician")
        cls.technician = User.objects.create_user(
            username="testtechnician", password="password"
        )
        cls.technician.groups.add(cls.technician_group)
        cls.item_request = ItemRequest.objects.create(
            manufacturer="Test MFG",
            model_part_num="Reject Model",
            quantity_requested=1,
            unit_price=0.01,
            requested_by=cls.technician,
        )
        cls.reject_url = reverse(
            "inventory:item_request_confirm_reject", kwargs={"pk": cls.item_request.pk}
        )

    def test_get_object(self):
        """
        Test that the correct object is returned in the context
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.reject_url)
        self.assertEqual(response.context["object"], self.item_request)

    def test_get_context_data(self):
        """
        Test the context data for the view
        """
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.reject_url)
        self.assertIn("object", response.context)
        self.assertEqual(response.context["object"], self.item_request)

    def test_post(self):
        """
        Test that the item request is rejected successfully.
        """
        self.client.login(username="testsuperuser", password="password")
        self.item_request.status_changed_by = self.superuser
        self.item_request.save()
        response = self.client.post(self.reject_url, {"Confirm": "Confirm"})
        self.assertEqual(response.status_code, 302)
        self.item_request.refresh_from_db()
        self.assertEqual(self.item_request.status, "Rejected")

    def test_post_cancel(self):
        """
        Test that the item request is not rejected when canceling.
        """
        self.client.login(username="testsuperuser", password="password")
        self.item_request.status_changed_by = self.superuser
        self.item_request.save()
        response = self.client.post(self.reject_url, {"Cancel": "Cancel"})
        self.assertEqual(response.status_code, 302)
        self.item_request.refresh_from_db()
        self.assertNotEqual(self.item_request.status, "Rejected")


class ItemRequestDeleteViewTests(TestCase):
    """
    Tests for ItemRequestDeleteView
    """

    # TODO: Tests for ItemRequestDeleteView
    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """


###################################################################################################
# Tests for the Views for the UsedItem Model ######################################################
###################################################################################################
class UsedItemViewTests(TestCase):
    """
    Tests for UsedItemView
    """

    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.technician_group = Group.objects.get(name="Technician")
        cls.intern_group = Group.objects.get(name="Intern")
        cls.viewer_group = Group.objects.get(name="Viewer")

        cls.superuser = User.objects.create_user(
            username="testsuperuser", password="password"
        )
        cls.superuser.groups.add(cls.superuser_group)
        cls.technician = User.objects.create_user(
            username="testtechnician", password="password"
        )
        cls.technician.groups.add(cls.technician_group)
        cls.intern = User.objects.create_user(
            username="testintern", password="password"
        )
        cls.intern.groups.add(cls.intern_group)
        cls.viewer = User.objects.create_user(
            username="testviewer", password="password"
        )
        cls.viewer.groups.add(cls.viewer_group)

        items = [
            Item(
                manufacturer="Fluke", model="Dials", part_or_unit=Item.UNIT, quantity=17
            ),
            Item(
                manufacturer="Fluke",
                model="45",
                part_or_unit=Item.PART,
                part_number="814137 Rev 2",
                quantity=10,
            ),
            Item(
                manufacturer="Amprobe",
                model="Bodys",
                part_or_unit=Item.PART,
                part_number="ACDC-100 TRMS",
                quantity=20,
            ),
        ]
        Item.objects.bulk_create(items)
        cls.item1 = Item.objects.filter(pk=1).first()
        cls.item2 = Item.objects.filter(pk=2).first()
        cls.item3 = Item.objects.filter(pk=3).first()

        used_items = [
            UsedItem(item=cls.item1, work_order=1234567, used_by=cls.technician),
            UsedItem(item=cls.item1, work_order=1010101, used_by=cls.superuser),
            UsedItem(item=cls.item2, work_order=1234567, used_by=cls.technician),
            UsedItem(item=cls.item3, work_order=5135265, used_by=cls.technician),
            UsedItem(item=cls.item3, work_order=1234567, used_by=cls.technician),
        ]
        UsedItem.objects.bulk_create(used_items)

        cls.used_items_url = reverse("inventory:used_items")

        cls.client = Client()
        cls.factory = RequestFactory()

    @tag("critical")
    def test_used_item_view_access_control(self):
        """
        Test that only superusers and technicians have access to UsedItemView
        """
        # Unauthenticated users don't have access (should redirect to login)
        response = self.client.get(self.used_items_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

        # Superusers have access
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.used_items_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        # Technicians have access
        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.used_items_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        # Interns have access
        self.client.login(username="testintern", password="password")
        response = self.client.get(self.used_items_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        # Viewers have access
        self.client.login(username="testviewer", password="password")
        response = self.client.get(self.used_items_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_get_queryset(self):
        """
        Test the queryset for the item requests.
        """
        request = self.factory.get(self.used_items_url)
        view = UsedItemView()
        view.request = request
        queryset = view.get_queryset()

        expected_ordered_used_items = [
            (self.item3.pk, 1234567),
            (self.item3.pk, 5135265),
            (self.item2.pk, 1234567),
            (self.item1.pk, 1010101),
            (self.item1.pk, 1234567),
        ]
        actual_ordered_used_items = list(queryset.values_list("item", "work_order"))

        self.assertEqual(queryset.count(), 5)
        self.assertEqual(actual_ordered_used_items, expected_ordered_used_items)


class UsedItemDetailViewTests(TestCase):
    """
    Tests for UsedItemDetailView
    """

    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.technician_group = Group.objects.get(name="Technician")
        cls.technician = User.objects.create_user(
            username="testtechnician", password="password"
        )
        cls.technician.groups.add(cls.technician_group)

        cls.generic_user = User.objects.create_user(
            username="testuser", password="password"
        )

        cls.item = Item.objects.create(
            manufacturer="Chroma",
            # model : "N/A"
            part_or_unit=Item.PART,
            part_number="G53 003700",
            description="Fan part",
            # location : "N/A"
            quantity=50,
            # min_quantity : 0
            unit_price=0.80,
        )
        cls.used_item = UsedItem.objects.create(
            item=cls.item,
            work_order=1234568,
            # datetime automatically set
            used_by=cls.technician,
        )
        cls.used_item_detail_url = reverse(
            "inventory:used_item_detail", kwargs={"pk": cls.used_item.pk}
        )

        cls.client = Client()
        cls.factory = RequestFactory()

    @tag("critical")
    def test_used_item_detail_view_access_control(self):
        """
        Test that only logged-in users can access the UsedItemDetailView.
        """
        response = self.client.get(self.used_item_detail_url)
        self.assertFalse(
            response.wsgi_request.user.is_authenticated,
            "The user is unexpectedly authenticated.",
        )
        self.assertEqual(
            response.status_code,
            302,
            "Unauthenticated user unexpectedly gained access to the UsedItem detail page.",
        )

        self.client.login(username="testuser", password="password")
        response = self.client.get(self.used_item_detail_url)
        self.assertEqual(
            response.status_code,
            200,
            "Authenticated user failed to access the UsedItem detail page.",
        )


class UsedItemCreateViewTests(TestCase):
    """
    Tests for UsedItemCreateView
    """

    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        # Create a superuser
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.superuser = User.objects.create_user(
            username="testsuperuser", password="password"
        )
        cls.superuser.groups.add(cls.superuser_group)

        # Create a technician user
        cls.technician_group = Group.objects.get(name="Technician")
        cls.technician = User.objects.create_user(
            username="testtechnician", password="password"
        )
        cls.technician.groups.add(cls.technician_group)

        # Create an intern user
        cls.intern_group = Group.objects.get(name="Intern")
        cls.intern = User.objects.create_user(
            username="testintern", password="password"
        )
        cls.intern.groups.add(cls.intern_group)

        # Create a viewer user
        cls.viewer_group = Group.objects.get(name="Viewer")
        cls.viewer = User.objects.create_user(
            username="testviewer", password="password"
        )
        cls.viewer.groups.add(cls.viewer_group)

        # Items for testing
        items = [
            Item(
                manufacturer="Fluke", model="Dials", part_or_unit=Item.UNIT, quantity=0
            ),
            Item(
                manufacturer="Fluke",
                model="45",
                part_or_unit=Item.PART,
                part_number="814137 Rev 2",
                quantity=1,
            ),
        ]
        Item.objects.bulk_create(items)
        cls.item1 = Item.objects.filter(pk=1).first()
        cls.item2 = Item.objects.filter(pk=2).first()
        cls.item1_use_url = (
            reverse("inventory:item_use_form") + f"?item_id={cls.item1.pk}"
        )
        cls.item2_use_url = (
            reverse("inventory:item_use_form") + f"?item_id={cls.item2.pk}"
        )

        cls.client = Client()
        cls.factory = RequestFactory()

    @tag("critical")
    def test_used_item_create_view_access_control(self):
        """
        Test that only superusers and technicians can access the UsedItemCreateView.
        """
        # Superuser access
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.item2_use_url)
        self.assertEqual(
            response.status_code,
            200,
            "Superuser failed to access the UsedItemCreateView.",
        )
        self.client.logout()

        # Technician access
        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.item2_use_url)
        self.assertEqual(
            response.status_code,
            200,
            "Technician failed to access the UsedItemCreateView.",
        )
        self.client.logout()

        # Intern forbidden
        self.client.login(username="testintern", password="password")
        response = self.client.get(self.item2_use_url)
        self.assertEqual(
            response.status_code,
            403,
            "Intern was able to access the UsedItemCreateView.",
        )
        self.client.logout()

        # Viewer forbidden
        self.client.login(username="testviewer", password="password")
        response = self.client.get(self.item2_use_url)
        self.assertEqual(
            response.status_code,
            403,
            "Viewer was able to access the UsedItemCreateView.",
        )
        self.client.logout()

    def test_dispatch(self):
        """
        Test the dispatch method of the UsedItemCreateView.
        """
        # Items with quantity > 0 can be used
        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.item2_use_url)
        self.assertEqual(response.status_code, 200)

        # Items with quantity == 0 cannot be used (should redirect or error)
        response = self.client.get(self.item1_use_url)
        self.assertNotEqual(response.status_code, 200)

    def test_form_valid(self):
        """
        Test that the form_valid function works as expected.
        """
        self.client.login(username="testtechnician", password="password")
        # Use item2 (quantity=1)
        response = self.client.post(
            self.item2_use_url,
            {
                "item": self.item2.pk,
                "work_order": 123456,
                "used_by": self.technician.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        item = Item.objects.get(pk=self.item2.pk)
        self.assertEqual(item.quantity, 0)
        # Check that the latest UsedItem exists
        used_item = UsedItem.objects.filter(item=item, work_order=123456).first()
        self.assertIsNotNone(used_item)
        # Check that the `used_by` field is set correctly
        self.assertEqual(used_item.used_by, self.technician)
        # Check that the latest ItemHistory record is for "use"
        history = ItemHistory.objects.filter(item=item).order_by("-timestamp").first()
        self.assertIsNotNone(history)
        self.assertEqual(history.action, "use")


class UsedItemDeleteViewTests(TestCase):
    """
    Tests for UsedItemDeleteView
    """

    @classmethod
    def setUpTestData(cls):
        """
        Setup
        """
        cls.superuser_group = Group.objects.get(name="Superuser")
        cls.technician_group = Group.objects.get(name="Technician")
        cls.intern_group = Group.objects.get(name="Intern")
        cls.viewer_group = Group.objects.get(name="Viewer")
        cls.superuser = User.objects.create_superuser(
            username="testsuperuser", password="password"
        )
        cls.superuser.groups.add(cls.superuser_group)
        cls.technician = User.objects.create_user(
            username="testtechnician", password="password"
        )
        cls.technician.groups.add(cls.technician_group)
        cls.intern = User.objects.create_user(
            username="testintern", password="password"
        )
        cls.intern.groups.add(cls.intern_group)
        cls.viewer = User.objects.create_user(
            username="testviewer", password="password"
        )
        cls.viewer.groups.add(cls.viewer_group)

        cls.item = Item.objects.create(
            manufacturer="Test",
            model="Test",
            part_or_unit=Item.PART,
            part_number="123",
            quantity=1,
        )
        cls.used_item = UsedItem.objects.create(
            item=cls.item,
            work_order=8888888,
            used_by=cls.technician,
        )
        cls.used_item_delete_url = reverse(
            "inventory:used_item_confirm_delete", kwargs={"pk": cls.used_item.pk}
        )

        cls.client = Client()
        cls.factory = RequestFactory()

    @tag("critical")
    def test_used_item_delete_view_access_control(self):
        """
        Test that only superusers and technicians can access the UsedItemDeleteView.
        """
        # Superuser access
        self.client.login(username="testsuperuser", password="password")
        response = self.client.get(self.used_item_delete_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        # Technician access
        self.client.login(username="testtechnician", password="password")
        response = self.client.get(self.used_item_delete_url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        # Intern forbidden
        self.client.login(username="testintern", password="password")
        response = self.client.get(self.used_item_delete_url)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # Viewer forbidden
        self.client.login(username="testviewer", password="password")
        response = self.client.get(self.used_item_delete_url)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_get_context_data(self):
        """
        Test the context data for the UsedItemDeleteView.
        """
        # Log in
        self.client.login(username="testsuperuser", password="password")
        # Simulate GET request
        response = self.client.get(self.used_item_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("object", response.context)
        self.assertEqual(response.context["object"], self.used_item)
