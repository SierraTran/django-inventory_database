from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import generic

from .models import Item


# Create your views here.
# @login_required
class ItemView(generic.ListView):
    template_name = "items.html"
    context_object_name = "items_list"

    def get_queryset(self):
        return Item.objects.all()


# @login_required
class ItemDetailsView(generic.ListView):
    model = Item
    template_name = "item-details.html"
    

    def get_queryset(self):
        
        return Item.objects.all()
