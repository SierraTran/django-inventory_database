from django.db import models
from django.core.validators import MinValueValidator
from django.urls import reverse

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
    min_quantity = models.IntegerField(
        default=0, validators=[MinValueValidator(0)]
    )
    unit_price = models.DecimalField(
        default=0.01,
        max_digits=16,
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
    )

    @property
    def low_stock(self):
        return self.quantity <= self.min_quantity

    def get_absolute_url(self):
        return reverse("inventory:item_detail", kwargs={"pk": self.pk})
    
    def __str__(self):
        """
        The string representation of the `Item` object

        Parameters:
            self (Item): The current `Item` object

        Returns:
            str: The `manufacturer`, a comma, `model`, and `part_number` if applicable.

        Example:
            "HP, 87 Case"
        """
        item_string = self.manufacturer + ", " + self.model
        if self.part_or_unit == self.PART:
            item_string += " " + self.part_number
        return item_string

class ItemRequest(models.Model):
    ACCEPTED = "Accepted"
    PENDING = "Pending"
    REJECTED = "Rejected"
    
    STATUS_CHOICES = {
        ACCEPTED: "Accepted",
        PENDING: "Pending",
        REJECTED: "Rejected"
    }
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity_requested = models.IntegerField()
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, default=PENDING, max_length=9)
    
class UsedItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    work_order = models.IntegerField()
    
    def get_absolute_url(self):
        return reverse("inventory:used_item_detail", kwargs={"pk": self.pk})
    
    def __str__(self):
        return "Work Order: " + str(self.work_order) + " | Item: " + str(self.item)