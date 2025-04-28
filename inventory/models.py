from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from model_utils.fields import StatusField
from model_utils import Choices, FieldTracker


# Create your models here.
class Item(models.Model):
    """ 
    This model represents an item in the inventory database.    

    Attributes:
        manufacturer (CharField): The name of the item's manufacturer. Defaults to "N/A" 
        model (CharField): The name of the item's model. Defaults to "N/A" 
        part_or_unit (CharField): Indicates whether the item is classified as a 'Part' or a 'Unit'. Defaults to 'Part' 
        part_number (CharField): The part number of the item. Can be blank if the item is a unit. 
        description (TextField): The description of the item 
        location (CharField): The physical location of the item 
        quantity (IntegerField): The quantity of the item in inventory 
        min_quantity (IntegerField): The minimum quantity of the item to keep in inventory 
        unit_price (DecimalField): The price of one of this item 
        last_modified_by (ForeignKey): The User that last edited the item through creating or updating 

    Tracking:
        tracker (FieldTracker): Tracks changes to the following fields: 
            - "manufacturer" 
            - "model" 
            - "part_or_unit" 
            - "part_number" 
            - "description" 
            - "location" 
            - "quantity" 
            - "min_quantity" 
            - "unit_price"  

    Properties: 
        low_stock (boolean): Indicates whether the item quantity is below the minimum quantity  
        model_part_num (str): The model and part number together 

    Meta: 
        db_table: Specifies the name of the database table for the item to be stored in 
        managed: Indicates whether Django will manage the lifecycle of the table during migrations (True) or not (False). 

    Methods: 
        `get_absolute_url()`: Resolves the URL for viewing the Item 
        `save()`: Overrides the save method in the Item model to set the modified_by field 
        `__str__()`: Represents the Item object as a string
    """
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
    def low_stock(self) -> bool:
        return self.quantity <= self.min_quantity

    @property
    def model_part_num(self) -> str:
        return f"{self.model} {self.part_number}"

    def get_absolute_url(self) -> str:
        """
        Resolves the URL for viewing the Item.

        Returns:
            str: The URL path of the Item object
        """
        return reverse("inventory:item_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs) -> None:
        """
        Overrides the save method in the Item model to set the last_modified_by field.
        """
        user = kwargs.pop("user", None)
        if user:
            self.last_modified_by = user
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        The string representation of the Item object

        Returns:
            str: The `manufacturer`, a comma, `model`, and `part_number` if applicable.
        """
        item_string = self.manufacturer + ", " + self.model
        if self.part_or_unit == self.PART:
            item_string += " " + self.part_number
        return item_string


class ItemHistory(models.Model):
    """
    This model represents an Item History object.

    Attributes:
        item (ForeignKey): The Item that is the subject of the history 
        action (CharField): The action that was done onto the item. It can be "Create", "Update", or "Use" 
        timestamp (DateTimeField): The date and time that the action took place 
        user (ForeignKey): The User that did the action 
        changes (TextField) : The details of the action explaining what happened 

    Methods:
        `__str__()`: _description_
        
    Meta: 
        verbose_name (str): The human readable name for ItemHistory 
        verbose_name_plural (str): The plural version of ItemHistory's human readable name 
        db_table (str): Specifies the name of the database table for the Item History to be stored in 
        managed (bool): Indicates whether Django will manage the lifecycle of the table during migrations (True) or not (False). 
    """
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
    """
    This model represents an item request in the database 

    Attributes: 
        manufacturer (CharField): The name of the manufacturer of the item 
        model_part_num (CharField): The model and part number of the item 
        quantity_requested (IntegerField): The quantity of the item being requested 
        description (TextField): The description of the item 
        unit_price (DecimalField): The price of one of this item 
        requested_by (ForeignKey): The User requesting the item. Limited to users in the technician group 
        timestamp (DateTimeField): The date and time that the request was made 
        status (StatusField): The status of the item request, which can be "Pending", "Accepted", or "Rejected". Defaults to "Pending".  
        status_changed_by (ForeignKey): The User who "accepted" or "rejected" the item request. Limited to users in the superuser group 

    Methods: 
        `get_absolute_url()`: Resolves the URL for viewing the ItemRequest object  
        `__str__()`: Represents the ItemRequest object as a string  

    Meta: 
        verbose_name (str): The human readable name for ItemRequest 
        verbose_name_plural (str): The plural version of ItemRequest's human readable name 
        db_table (str): Specifies the name of the database table for the Item Request to be stored in  
        managed (bool): Indicates whether Django will manage the lifecycle of the table during migrations (True) or not (False)
    """
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
        decimal_places=2, max_digits=14, validators=[MinValueValidator(Decimal("0.01"))]
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

    def get_absolute_url(self) -> str:
        """
        Resolves the URL for viewing the ItemRequest object.

        Returns:
            str: _description_
        """
        return reverse("inventory:item_request_detail", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        """
        Represents the ItemRequest object as a string.

        Returns:
            str: _description_
        """
        return f"Request by {self.requested_by} for {self.manufacturer}, {self.model_part_num}"


class UsedItem(models.Model):
    """
    This model represents a used item in the database 

    Attributes: 
        item (ForeignKey): The Item from the inventory that has been used 
        work_order (IntegerField): The work order that the item has been used in 
        datetime_used (DateTimeField): The date and time that the item has been used 
        used_by (ForeignKey): The User that used the item 
        
    Methods:
        `get_absolute_url()`: Resolves the URL for viewing the UsedItem object  
        `__str__()`: Represents the UsedItem object as a string 
        
    Meta:
        verbose_name (str): The human readable name for UsedItem 
        verbose_name_plural (str): The plural version of UsedItem's human readable name 
        db_table (str): Specifies the name of the database table for the Item Request to be stored in  
        managed (bool): Indicates whether Django will manage the lifecycle of the table during migrations (True) or not (False)
    """
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
        """
        Resolves the URL for viewing the UsedItem object  

        Returns:
            str: _description_
        """
        return reverse("inventory:used_item_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"Work Order: {self.work_order} | Item: {self.item}"


class PurchaseOrderItem(models.Model):
    """

    """
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
