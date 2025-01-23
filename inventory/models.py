from django.db import models

# Create your models here.
class item(models.Model):
    ItemType = models.TextChoices("ItemType", "Part Unit")

    manufacturer = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    part_or_unit = models.CharField(blank=False, choices=ItemType, max_length=10)
    description = models.TextField()
    location = models.CharField(max_length=50)
    quantity = models.IntegerField()
    price = models.CharField(max_length=255)
    