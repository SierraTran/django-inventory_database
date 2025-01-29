from django.db import models
from django.core.validators import MinValueValidator


# Create your models here.
class Item(models.Model):
    ItemType = models.TextChoices("ItemType", "Part Unit")

    manufacturer = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    part_or_unit = models.CharField(blank=False, choices=ItemType, max_length=10)
    part_number = models.CharField(blank=True, max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    price = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=0.01,
        validators=[MinValueValidator(0.00)],
    )

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
        return self.manufacturer + ", " + self.model + " " + self.part_number
