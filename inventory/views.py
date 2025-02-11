from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from django.shortcuts import render
from django.core.paginator import Paginator

from haystack.query import SearchQuerySet

from .models import Item


# Create your views here.
class ItemView(LoginRequiredMixin, ListView):
    """
    View to list all items.

    Attributes:
        paginate_by (int): Number of items to display per page.
        model (Model): The model that this view will display.
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
        return Item.objects.all().order_by("manufacturer", "model", "part_number")


class ItemDetailView(LoginRequiredMixin, DetailView):
    """
    Class-based view for displaying the details of a single item.
    This view requires the user to be logged in and inherits from LoginRequiredMixin
    and DetailView.

    Attributes:
        model (Item): The model that this view will operate on.
        template_name (str): The template used to render the detail view.
        
    Methods:
        get_context_data(**kwargs): Adds the user's group to the context data.
    """
    model = Item
    template_name = "item_detail.html"

    def get_context_data(self, **kwargs):
        """
        Adds the user's group to the context data.

        Returns:
            dict: The context data with the user's group added.
        """
        context = super().get_context_data(**kwargs)
        context["user_group"] = self.request.user.groups.first()
        return context


class ItemCreateView(UserPassesTestMixin, CreateView):
    """
    Class-based view for creating a new item.
    This view requires the user to be in the 'Technician' group.

    Attributes:
        model (Item): The model that this view will operate on.
        fields (list): The fields to be displayed in the form.
        template_name (str): The template used to render the form.
    """
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
        Checks if the user is in the 'Superuser' group.

        Returns:
            bool: True if the user is in the 'Superuser' group, False otherwise.
        """
        return self.request.user.groups.first().name == "Superuser"


class ItemUpdateView(UserPassesTestMixin, UpdateView):
    """
    Class-based view for updating an existing item.
    This view requires the user to be in the 'Superuser' group.

    Attributes:
        model (Item): The model that this view will operate on.
        fields (list): The fields to be displayed in the form.
        template_name (str): The template used to render the form.
    """
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
        Checks if the user is in the 'Superuser' group.

        Returns:
            bool: True if the user is in the 'Superuser' group, False otherwise.
        """
        return self.request.user.groups.first().name == "Superuser"


class ItemQuantityUpdateView(UserPassesTestMixin, UpdateView):
    """
    Class-based view for updating the quantity of an existing item.
    This view requires the user to be in the 'Intern' group.

    Attributes:
        model (Item): The model that this view will operate on.
        fields (list): The fields to be displayed in the form.
        template_name (str): The template used to render the form.
    """
    model = Item
    fields = ["quantity"]
    template_name = "item_update_form.html"

    def test_func(self):
        """
        Checks if the user is in the 'Intern' group.

        Returns:
            bool: True if the user is in the 'Intern' group, False otherwise.
        """
        return self.request.user.groups.first().name == "Intern"


class SearchItemsView(ListView):
    """
    Class-based view for searching items.
    This view uses Haystack to perform the search.

    Attributes:
        paginate_by (int): Number of items to display per page.
        model (Item): The model that this view will operate on.
        template_name (str): The template used to render the search results.
        context_object_name (str): The name of the context variable to use for the search results.

    Methods:
        get_queryset(): Retrieves the search results based on the query.
    """
    model = Item
    template_name = "search/search.html"
    context_object_name = "results_list"

    def get_queryset(self):
        """
        Retrieves the search results based on the query.

        Returns:
            list: A list of search results.
        """
        query = self.request.GET.get("q")
        results = (
            SearchQuerySet().filter(content=query).order_by("manufacturer", "model", "part_number") if query else []
        )
        return results
