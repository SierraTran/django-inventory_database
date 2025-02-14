from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView, DeleteView
from django.shortcuts import redirect
from haystack.query import SearchQuerySet
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy

import openpyxl

from .forms import ImportFileForm

from .models import Item, ItemRequest


# Create your views here.


##########################
# Views for the Item Model
##########################
class ItemView(LoginRequiredMixin, ListView):
    """
    Class-based view to list all items.
    The user is required to be logged in to access this view.

    Attributes:
        model (Item): The model that this view will display.
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
        Items are alphanumerically ordered (ascending) by `manufacturer` first, `model` second, and finally `part_number`.

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


class ItemCreateSuperuserView(UserPassesTestMixin, CreateView):
    """
    Class-based view for creating a new item.
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
        "min_quantity",
        "unit_price",
    ]
    template_name = "item_create_form.html"

    def test_func(self) -> bool:
        """
        Checks if the user is in the 'Superuser' group.

        Returns:
            bool: True if the user is in the 'Superuser' group, False otherwise.
        """
        return self.request.user.groups.first().name == "Superuser"


class ItemCreateTechnicianView(UserPassesTestMixin, CreateView):
    """
    Class-based view for creating a new item.
    This view requires the user to be in the 'Technician' group.

    Attributes:
        model (Item): The model that this view will operate on.
        fields (list[str]): The fields to be displayed in the form.
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
        "unit_price",
    ]
    template_name = "item_create_form.html"

    def test_func(self) -> bool:
        """
        Checks if the user is in the 'Technician' group.

        Returns:
            bool: True if the user is in the 'Technician' group, False otherwise.
        """
        return self.request.user.groups.first().name == "Technician"


class ItemUpdateSuperuserView(UserPassesTestMixin, UpdateView):
    """
    Class-based view for updating an existing item.
    This view requires the user to be in the "Superuser" or "Technician" group.

    Attributes:
        model (Item): The model that this view will operate on.
        fields (list[str]): The fields to be displayed in the form.
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
        "min_quantity",
        "unit_price",
    ]
    template_name = "item_update_form.html"

    def test_func(self) -> bool:
        """
        Checks if the user is in the "Superuser" group.

        Returns:
            bool: True if the user is in the "Superuser" group, False otherwise.
        """
        user_group_name = self.request.user.groups.first().name
        return user_group_name == "Superuser"


class ItemUpdateTechnicianView(UserPassesTestMixin, UpdateView):
    """
    Class-based view for updating an existing item.
    This view requires the user to be in the "Technician" group.

    Attributes:
        model (Item): The model that this view will operate on.
        fields (list[str]): The fields to be displayed in the form.
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
        "unit_price",
    ]
    template_name = "item_update_form.html"

    def test_func(self) -> bool:
        """
        Checks if the user is in the "Technician" group.

        Returns:
            bool: True if the user is in the "Technician" group, False otherwise.
        """
        user_group_name = self.request.user.groups.first().name
        return user_group_name == "Technician"


class ItemUpdateInternView(UserPassesTestMixin, UpdateView):
    """
    Class-based view for updating the quantity of an existing item.
    This view requires the user to be in the "Intern" group.

    Attributes:
        model (Item): The model that this view will operate on.
        fields (list[str]): The fields to be displayed in the form. For interns, only the quantity is available to them.
        template_name (str): The template used to render the form.
    """

    model = Item
    fields = ["quantity"]
    template_name = "item_update_form.html"

    def test_func(self) -> bool:
        """
        Checks if the user is in the "Intern" group.

        Returns:
            bool: True if the user is in the "Intern" group, False otherwise.
        """
        return self.request.user.groups.first().name == "Intern"


class ItemDeleteView(UserPassesTestMixin, DeleteView):
    """
    Class-based view for deleting an existing item.
    This view requires the user to be in the "Superuser" or "Technician" group.

    Attributes:
        model (Item): The model that this view will operate on.
        tempalte_name (str): The name of the tempalte that the view will render
        success_url (str): The URL to redirect to upon successful deletion.
        fail_url (str): The URL to redirect to if the deletion is cancelled.

    Methods:
        test_func(): Checks if the user is in the "Superuser" or "Technician" group
        post(request, *args, **kwargs): Handles POST requests to delete the item or cancel the deletion.
    """

    model = Item
    template_name = "inventory/item_confirm_delete.html"
    success_url = reverse_lazy("inventory:items")

    def get_fail_url(self):
        return reverse_lazy(
            "inventory:item_detail", kwargs={"pk": self.get_object().pk}
        )

    fail_url = property(get_fail_url)

    def test_func(self) -> bool:
        """
        Checks if the user is in the "Superuser" or "Technician" group.

        Returns:
            bool: True if the user is in the "Superuser" or "Technician" group, False otherwise.
        """
        user_group_name = self.request.user.groups.first().name
        return user_group_name in ["Superuser", "Technician"]

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to delete the item or cancel the deletion.

        Args:
            request (_type_): _description_

        Returns:
            _type_: _description_
        """
        if "Cancel" in request.POST:
            url = self.fail_url
            return redirect(url)
        else:
            # messages.success(self.request, "The item was deleted successfully.")
            return super(ItemDeleteView, self).post(request, *args, **kwargs)


class SearchItemsView(ListView):
    """
    Class-based view for searching items.
    This view uses Haystack to perform the search.

    Attributes:
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
            SearchQuerySet()
            .filter(content=query)
            .order_by("manufacturer", "model", "part_number")
            if query
            else []
        )
        return results


class ImportItemDataView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    """
    Renders a view to allow users to import items from an .xls file to the database.

    Attributes:
        form_class:
        template_name (str): The name of the template to be rendered by the class.

    Methods:
        test_func(): Checks if the user is in the "Superuser" or "Technician" group.
        form_valid(form): Processes data from an uploaded Excel file to the database.
    """

    form_class = ImportFileForm
    template_name = "import_item_data.html"

    def test_func(self) -> bool:
        """
        Checks if the user is in the "Superuser" or "Technician" group.

        Returns:
            bool: True if the user is in the "Superuser" or "Technician" group, False otherwise.
        """
        user_group_name = self.request.user.groups.first().name
        return user_group_name in ["Superuser", "Technician"]

    def form_valid(self, form) -> HttpResponseRedirect:
        """
        Processes the uploaded Excel file from the form, extracts item data from each row,
        and creates Item objects in the database.
        Empty cells will have a default value set for them in the database.

        Args:
            form (Form): The form containing the uploaded Excel file.

        Returns:
            HttpResponseRedirect: Redirects to the items list view after processing the file.
        """
        file = form.cleaned_data["file"]
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active
        # For each record in the excel file ...
        for row in sheet.iter_rows(min_row=2, values_only=True):
            # Get its data. Set to default value if None
            manufacturer = row[0] if row[0] is not None else "N/A"
            model = row[1] if row[1] is not None else "N/A"
            part_or_unit = row[2] if row[2] is not None else "Part"
            part_number = row[3] if row[3] is not None else ""
            description = (
                row[4] if row[4] is not None else str(model) + " " + str(part_number)
            )
            location = row[5] if row[5] is not None else "N/A"
            quantity = row[6] if row[6] is not None else 0
            min_quantity = row[7] if row[7] is not None else 0
            unit_price = row[8] if row[8] is not None else 0.01

            # Create a new Item with the data
            Item.objects.create(
                manufacturer=manufacturer,
                model=model,
                part_or_unit=part_or_unit,
                part_number=part_number,
                description=description,
                location=location,
                quantity=quantity,
                min_quantity=min_quantity,
                unit_price=unit_price,
            )
        # Go to items page
        return HttpResponseRedirect(reverse("inventory:items"))


#################################
# Views for the ItemRequest Model
#################################
class ItemRequestView(UserPassesTestMixin, ListView):
    """
    Class-based view for displaying item requests.
    This view inherits from UserPassesTestMixin and ListView to display a list of item requests.
    Only users belonging to the "Technician" or "Superuser" groups are allowed to access this view.

    Attributes:
        model (ItemRequest): The model that this view will display.
        template_name (str): The template used to render the view.
        context_object_name (str): The context variable name for the list of item requests.

    Methods:
        test_func: Checks if the user belongs to the "Technician" or "Superuser" group.
        get_queryset: Returns the queryset of all item requests.
    """

    model = ItemRequest
    template_name = "item_requests.html"
    context_object_name = "item_requests_list"

    def test_func(self) -> bool:
        """
        Checks if the user belongs to the "Superuser" or "Technician" group.

        Returns:
            bool: True if the user is in the "Superuser" or "Technician" group, False otherwise.
        """
        user_group_name = self.request.user.groups.first().name
        return user_group_name in ["Superuser", "Technician"]

    def get_queryset(self):
        """
        Returns the queryset of all item requests.

        Returns:
            _description_
        """
        return ItemRequest.objects.all()


class ItemRequestCreateView(UserPassesTestMixin, CreateView):
    """
    Class-based view for creating an item request.
    This view requires the user to be in the "Technician" group.

    Attributes:
        model (ItemRequest): The model that this view will operate on.
        fields (list): The fields tp be displayed in the form.
        template_name (str): The template used to render the form.
    """

    model = ItemRequest
    fields = [
        "item",
        "quantity_requested",
        "requested_by",
        "status",
    ]
    template_name = "item_request_form.html"

    def test_func(self) -> bool:
        """
        Checks if the user is in the "Technician" group.

        Returns:
            bool: True if the user is in the "Technician" group, False otherwise.
        """
        return self.request.user.groups.first().name == "Technician"

    def get_context_data(self, **kwargs):
        """
        Adds the specific item to the context data.

        Returns:
            dict: The context data with the specific item added.
        """
        context = super().get_context_data(**kwargs)
        item_id = self.kwargs.get("pk")
        context["item"] = Item.objects.get(pk=item_id)
        return context
