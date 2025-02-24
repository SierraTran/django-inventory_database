from django.db import models
from django.core.validators import MinValueValidator
from django.urls import reverse

from model_utils.fields import StatusField, MonitorField
from model_utils import Choices, FieldTracker

from authentication.models import User


# Create your models here.
class Item(models.Model):
    PART = "Part"
    UNIT = "Unit"

    ITEM_TYPE_CHOICES = {
        PART: "Part",
        UNIT: "Unit",
    }

    manufacturer = models.CharField(default="N/A", max_length=50)
    model = models.CharField(default="N/A", max_length=100)
    part_or_unit = models.CharField(
        blank=False,
        choices=ITEM_TYPE_CHOICES,
        default=PART,
        max_length=5,
    )
    part_number = models.CharField(blank=True, max_length=100)
    description = models.TextField()
    location = models.CharField(default="N/A", max_length=50)
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    min_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(
        default=0.01,
        max_digits=16,
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
    )

    last_modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    
    tracker = FieldTracker(fields=[
        'manufacturer', 'model', 'part_or_unit', 'part_number', 'description',
        'location', 'quantity', 'min_quantity', 'unit_price'
    ])

    @property
    def low_stock(self):
        return self.quantity <= self.min_quantity

    def get_absolute_url(self):
        return reverse("inventory:item_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        """
        Overrides the save method in the Item model to set the modified_by field.
        """
        user = kwargs.pop('user', None)
        if user:
            self.modified_by = user
        super().save(*args, **kwargs)

    def __str__(self):
        """
        The string representation of the `Item` object

        Parameters:
            self (Item): The current `Item` object

        Returns:
            str: The `manufacturer`, a comma, `model`, and `part_number` if applicable.
        """
        item_string = self.manufacturer + ", " + self.model
        if self.part_or_unit == self.PART:
            item_string += " " + self.part_number
        return item_string


class ItemHistory(models.Model):
    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    action = models.CharField(max_length=6, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.item} - {self.action} - {self.timestamp}"


class ItemRequest(models.Model):
    STATUS = Choices("Pending", "Accepted", "Rejected")

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity_requested = models.IntegerField()
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = StatusField(db_index=True)


class UsedItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    work_order = models.IntegerField()

    def get_absolute_url(self):
        return reverse("inventory:used_item_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return "Work Order: " + str(self.work_order) + " | Item: " + str(self.item)
