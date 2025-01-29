from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import generic

from .models import Item


# Create your views here.
# @login_required
class ItemView(generic.ListView):
    """
    View to list all items.
    
    Attributes:
        template_name (str): The name of the template to use for rendering the view.
        context_object_name (str): The name of the context variable to use for the list of items.
    Methods:
        get_queryset(): Retrieves the list of items to be displayed.
    """
    template_name = "items.html"
    context_object_name = "items_list"

    def get_queryset(self):
        """
        Retrieves the list of items to be displayed.

        Returns:            
            QuerySet: A queryset containing all items.
        """
        return Item.objects.all()


# @login_required
class ItemDetailsView(generic.ListView):
    model = Item
    template_name = "item-details.html"
    context_object_name = "item"
    
    


def getItemDetails(request, pk):
    item = get_object_or_404(Item, pk=pk).__dict__

    return render(request, "item-details.html", item)
