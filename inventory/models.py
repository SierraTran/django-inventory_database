from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from model_utils.fields import StatusField
from model_utils import Choices, FieldTracker


# Create your models here.
class Item(models.Model):
    class Meta:
        db_table = "inventory_item"
        managed = True

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
    description = models.TextField(blank=True)
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

    tracker = FieldTracker(
        fields=[
            "manufacturer",
            "model",
            "part_or_unit",
            "part_number",
            "description",
            "location",
            "quantity",
            "min_quantity",
            "unit_price",
        ]
    )

    @property
    def low_stock(self):
        return self.quantity <= self.min_quantity

    @property
    def model_part_num(self):
        return f"{self.model} {self.part_number}"

    def get_absolute_url(self):
        return reverse("inventory:item_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        """
        Overrides the save method in the Item model to set the last_modified_by field.
        """
        user = kwargs.pop("user", None)
        if user:
            self.last_modified_by = user
        super().save(*args, **kwargs)

    def __str__(self):
        """
        The string representation of the `Item` object

        Returns:
            str: The `manufacturer`, a comma, `model`, and `part_number` if applicable.
        """
        item_string = self.manufacturer + ", " + self.model
        if self.part_or_unit == self.PART:
            item_string += " " + self.part_number
        return item_string


class ItemHistory(models.Model):
    class Meta:
        verbose_name = "Item History"
        verbose_name_plural = "Item Histories"
        db_table = "inventory_itemhistory"
        managed = True

    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("use", "Use"),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    action = models.CharField(max_length=6, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changes = models.TextField(null=True, blank=True)

    def __str__(self):
        local_timestamp = timezone.localtime(self.timestamp) 
        formatted_timestamp = local_timestamp.strftime("%Y-%m-%d %I:%M:%S %p")
        return f"{self.item} - {self.action} - {formatted_timestamp}"


class ItemRequest(models.Model):
    class Meta:
        verbose_name = "Item Request"
        verbose_name_plural = "Item Requests"
        db_table = "inventory_itemrequest"
        managed = True

    STATUS = Choices("Pending", "Accepted", "Rejected")

    manufacturer = models.CharField(
        max_length=100,
        blank=True,
    )
    model_part_num = models.CharField(max_length=100, blank=True)
    quantity_requested = models.IntegerField(validators=[MinValueValidator(1)])
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(
        decimal_places=2, max_digits=14, validators=[MinValueValidator(0.01)]
    )
    requested_by = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"groups__name": "Technician"}, related_name="requested_by_user"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    status = StatusField(db_index=True, default="Pending")
    status_changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        limit_choices_to={"groups__name": "Superuser"},
        related_name="status_changed_by_user"
    )
    
    tracker = FieldTracker(fields=['status'])

    def get_absolute_url(self):
        return reverse("inventory:item_request_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"Request by {self.requested_by} for {self.manufacturer}, {self.model_part_num}"


class UsedItem(models.Model):
    class Meta:
        verbose_name = "Used Item"
        verbose_name_plural = "Used Items"
        db_table = "inventory_useditem"
        managed = True

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        error_messages={"required": "An Item is required."},
    )
    work_order = models.IntegerField(
        error_messages={"required": "A Work Order number is required."}
    )
    datetime_used = models.DateTimeField(default=timezone.now)
    used_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"groups__name__in": ["Technician", "Superuser"]},
    )

    def get_absolute_url(self):
        return reverse("inventory:used_item_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"Work Order: {self.work_order} | Item: {self.item}"


class PurchaseOrderItem(models.Model):
    class Meta:
        verbose_name = "Purchase Order Item"
        verbose_name_plural = "Purchase Order Items"
        db_table = "inventory_purchaseorderitem"
        managed = True

    manufacturer = models.CharField(max_length=100, blank=True)
    model_part_num = models.CharField(max_length=100, blank=True)
    quantity_ordered = models.IntegerField(validators=[MinValueValidator(0)])
    description = models.TextField(blank=True)
    serial_num = models.CharField(max_length=100, blank=True)
    property_num = models.CharField(max_length=100, blank=True)
    unit_price = models.DecimalField(
        decimal_places=2, max_digits=14, validators=[MinValueValidator(0.00)]
    )

    def __str__(self):
        return f"Purchase Order for {self.model_part_num} by {self.manufacturer} - Quantity: {self.quantity_ordered}"
