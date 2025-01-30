from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView
from django.db.models import Q, CharField

from .models import Item


# Create your views here.
# @login_required
class ItemView(ListView):
    """
    View to list all items.

    Attributes:
        template_name (str): The name of the template to use for rendering the view.
        context_object_name (str): The name of the context variable to use for the list of items.

    Methods:
        get_queryset(): Retrieves the list of items to be displayed.
    """

    model = Item
    template_name = "items.html"
    context_object_name = "items_list"

    def get_queryset(self):
        """
        Retrieves the list of items to be displayed.
        Items are alphanumerically ordered (ascending) by `manufacturer` first and model second.

        Returns:
            QuerySet: A queryset containing all items.
        """
        return Item.objects.all().order_by("model").order_by("manufacturer")


# @login_required
class ItemDetailsView(TemplateView):
    model = Item
    template_name = "item-details.html"
    context_object_name = "item"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


def getItemDetails(request, pk):
    item = get_object_or_404(Item, pk=pk)
    context = {"item": item}
    return render(request, "item-details.html", context)
