from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView
from django.db.models import Q, CharField

from .models import Item


# Create your views here.
class ItemView(LoginRequiredMixin, ListView):
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


class ItemDetailsView(LoginRequiredMixin, TemplateView):
    model = Item
    template_name = "item-details.html"
    context_object_name = "item"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


@login_required
def getItemDetails(request, pk):
    item = get_object_or_404(Item, pk=pk)
    current_user = request.user
    user_group = current_user.groups.first()  # Get the first group the user belongs to
    context = {
        "item": item,
        "user_group": user_group,
    }
    return render(request, "item-details.html", context)


# @login_required
# def filterItems(request):
#     query = request.GET.get('q')
#     part_or_unit = request.GET.get('part_or_unit')
#     items_list = Item.objects.all()

#     if query:
#         items_list = items_list.filter(
#             Q(manufacturer__icontains=query) |
#             Q(model__icontains=query) |
#             Q(part_number__icontains=query) |
#             Q(description__icontains=query)
#         )

#     if part_or_unit:
#         items_list = items_list.filter(part_or_unit=part_or_unit)

#     return render(request, 'items.html', {'items_list': items_list})
