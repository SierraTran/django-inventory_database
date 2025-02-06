from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from django.shortcuts import render

from haystack.query import SearchQuerySet

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
    paginate_by = 20
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
        return Item.objects.all().order_by("manufacturer", "model", "part_number")


class ItemDetailView(LoginRequiredMixin, DetailView):
    model = Item
    template_name = "item_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_group"] = self.request.user.groups.first()
        return context



class ItemCreateView(UserPassesTestMixin, CreateView):
    model = Item
    fields = [
        "manufacturer",
        "model",
        "part_or_unit",
        "part_number",
        "description",
        "location",
        "quantity",
        "price",
    ]
    template_name = "item_create_form.html"
    
    def test_func(self):
        """
        Checks if the user is in the 'Superuser' group

        Returns:
            Boolean: True if the user is in the 'Superuser' group. False if otherwise.
        """
        return self.request.user.groups.first().name == "Superuser"


class ItemUpdateView(UserPassesTestMixin, UpdateView):
    model = Item
    fields = [
        "manufacturer",
        "model",
        "part_or_unit",
        "part_number",
        "description",
        "location",
        "quantity",
        "price",
    ]
    template_name = "item_update_form.html"

    def test_func(self):
        """
        Checks if the user is in the 'Superuser' group

        Returns:
            Boolean: True if the user is in the 'Superuser' group. False if otherwise.
        """
        return self.request.user.groups.first().name == "Superuser"


class ItemQuantityUpdateView(UserPassesTestMixin, UpdateView):
    model = Item
    fields = ["quantity"]
    template_name = "item_update_form.html"

    def test_func(self):
        return self.request.user.groups.first().name == "Regular User"


def search_items(request):
    query = request.GET.get("q")
    results = (
        SearchQuerySet()
        .filter(content=query)
        .order_by("manufacturer", "model", "part_number")
        if query
        else []
    )
    context = {
        "results": results,
        "query": query,
    }
    return render(request, "search/search.html", context)

class SearchItemsView(ListView):
    paginate_by = 20
    model = Item
    template_name = "search/search.html"
    context_object_name = "results_list"
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        results = SearchQuerySet() \
                    .filter(content=query) \
                    .order_by("manufacturer", "model", "part_number") \
                    if query else []           
        return results


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
