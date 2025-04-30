import tempfile
from django.test import TestCase
from django.core.management import call_command
from haystack import connections
from haystack.query import SearchQuerySet
from haystack.signals import BaseSignalProcessor
from inventory.models import Item, UsedItem


class SearchIndexesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for search index tests.
        """
        # Create test objects
        cls.item1 = Item.objects.create(
            manufacturer="Test Manufacturer",
            model="Test Model 1",
            part_or_unit=Item.PART,
            part_number="12345",
            description="Test description 1",
            location="Shelf A",
            quantity=10,
            unit_price=100.50,
        )
        cls.item2 = Item.objects.create(
            manufacturer="Another Manufacturer",
            model="Test Model 2",
            part_or_unit=Item.UNIT,
            part_number="67890",
            description="Test description 2",
            location="Shelf B",
            quantity=5,
            unit_price=200.75,
        )
        cls.used_item = UsedItem.objects.create(
            item=cls.item1,
            work_order=1234567,
        )

        # Use a temporary directory for the Whoosh index
        cls.temp_dir = tempfile.TemporaryDirectory()

        # Override Haystack settings
        cls.settings_override = {
            "HAYSTACK_CONNECTIONS": {
                "default": {
                    "ENGINE": "haystack.backends.whoosh_backend.WhooshEngine",
                    "PATH": cls.temp_dir.name,
                },
            }
        }
        cls.settings_context = cls.settings(self=cls, **cls.settings_override)
        cls.settings_context.enable()

        # Update the search index
        call_command("update_index", verbosity=0)

    def test_item_indexing(self):
        """
        Test that Item objects are correctly indexed.
        """
        results = SearchQuerySet().models(Item).filter(content="Test Model")
        self.assertEqual(
            results.count(), 2, "The number of indexed items is incorrect."
        )

    def test_used_item_indexing(self):
        """
        Test that UsedItem objects are correctly indexed.
        """
        results = SearchQuerySet().models(UsedItem).filter(content="1234567")
        self.assertEqual(
            results.count(), 1, "The number of indexed used items is incorrect."
        )
        self.assertEqual(
            results[0].object, self.used_item, "The indexed used item is incorrect."
        )

    def test_empty_search(self):
        """
        Test that a search query with no matches returns no results.
        """
        results = SearchQuerySet().filter(content="Nonexistent Item")
        self.assertEqual(
            results.count(),
            0,
            "The search query returned results when it should not have.",
        )

    @classmethod
    def tearDownClass(cls):
        cls.settings_context.disable()
        cls.temp_dir.cleanup()  # Clean up the temporary directory
        super().tearDownClass()
