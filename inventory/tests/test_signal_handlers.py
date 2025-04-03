from django.test import Client, TestCase
from django.urls import reverse
from freezegun import freeze_time

from django.contrib.auth.models import User, Group
from inventory.models import Item, ItemHistory