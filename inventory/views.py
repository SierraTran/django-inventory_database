from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError
from django.forms import formset_factory
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from haystack.query import SearchQuerySet

from openpyxl import load_workbook

from .forms import ImportFileForm, UsedItemForm, PurchaseOrderItemFormSet

from .models import Item, ItemHistory, ItemRequest, PurchaseOrderItem, UsedItem

from .excel_functions import setup_worksheet


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


class ItemHistoryView(LoginRequiredMixin, ListView):
    """
    Class-based view for displaying the history of a specific item.
    This view requires the user to be logged in.

    Attributes:
        model (ItemHistory): The model that this view will operate on.
        template_name (str): The template used to render the history view.
        context_object_name (str): The context variable name for the list of item history records.

    Methods:
        get_queryset(): Retrieves the history records for the specific item.
        get_context_data(**kwargs): Adds the specific item to the context data.
    """

    model = ItemHistory
    template_name = "item_history.html"
    context_object_name = "item_history_list"

    def get_queryset(self):
        """
        Retrieves the history records for the specific item.

        Returns:
            QuerySet: The queryset containing the history records for the item.
        """
        item_id = self.kwargs["pk"]
        history = ItemHistory.objects.filter(item_id=item_id).order_by("-timestamp")
        return history

    def get_context_data(self, **kwargs):
        """
        Adds the specific item to the context data.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The context data with the specific item added.
        """
        item_id = self.kwargs["pk"]
        context = super().get_context_data(**kwargs)
        context["item"] = Item.objects.filter(id=item_id)[0]
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
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name == "Superuser"

    def form_valid(self, form):
        """
        Overrides the form_valid function of the parent class (`CreateView`) to add the user to the form.

        Args:
            form (ModelForm): The form that handles info about the created item.

        Returns:
            HttpResponse: The HTTP response object.
        """
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ItemCreateTechnicianView(UserPassesTestMixin, CreateView):
    """
    Class-based view for creating a new item.
    This view requires the user to be in the 'Technician' group.

    Attributes:
        model (Item): The model that this view will operate on.
        fields (list[str]): The fields to be displayed in the form.
        template_name (str): The template used to render the form.

    Methods:
        test_func(): Checks if the user is in the 'Technician' group.
        form_valid(form): Overrides form_valid to pass current user to save method
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
        user_group = self.request.user.group.first()
        return user_group is not None and user_group.name == "Technician"

    def form_valid(self, form):
        """
        Overrides the form_valid function of the parent class (`CreateView`) to pass the current user to the save method.

        Args:
            form (ModelForm): The form that handles the data for updating the Item object.

        Returns:
            HttpResponse: The HTTP response object.
        """
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ItemUpdateSuperuserView(UserPassesTestMixin, UpdateView):
    """
    Class-based view for updating an existing item as a Superuser.
    This view requires the user to be in the "Superuser" group.

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
        user_group = self.request.user.groups.first()
        user_group_name = user_group.name
        return user_group != None and user_group_name == "Superuser"

    def form_valid(self, form):
        """
        Overrides the form_valid function of the parent class (`UpdateView`) to pass the current user to the save method.

        Args:
            form (ModelForm): The form that handles the data for updating the Item object.

        Returns:
            HttpResponse: The HTTP response object.
        """
        form.instance.last_modified_by = self.request.user
        return super().form_valid(form)

    def save(self, *args, **kwargs):
        """
        Saves the updated item with additional keyword arguments.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: The HTTP response object.
        """
        kwargs["user"] = self.request.user
        return super().save(*args, **kwargs)


class ItemUpdateTechnicianView(UserPassesTestMixin, UpdateView):
    """
    Class-based view for updating an existing item as a Technician.
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

    def form_valid(self, form):
        """
        Overrides form_valid function of the parent class (`UpdateView`) to pass the current user to the save method.

        Args:
            form (ModelForm): The form that handles the data for updating the Item object.

        Returns:
            HttpResponse: The HTTP response object.
        """
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def save(self, *args, **kwargs):
        kwargs["user"] = self.request.user
        return super().save(*args, **kwargs)


class ItemUpdateInternView(UserPassesTestMixin, UpdateView):
    """
    Class-based view for updating the quantity of an existing item as an Intern.
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

    def form_valid(self, form):
        """
        Overrides the form_valid function of the parent class (`UpdateView`) to pass the current user to the save method.

        Args:
            form (ModelForm): The form that handles the data for updating the Item object.

        Returns:
            HttpResponse: The HTTP response object.
        """
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def save(self, *args, **kwargs):
        """
        Saves the updated item with additional keyword arguments.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: The HTTP response object.
        """
        kwargs["user"] = self.request.user
        return super().save(*args, **kwargs)


class ItemDeleteView(UserPassesTestMixin, DeleteView):
    """
    Class-based view for deleting an existing item.
    This view requires the user to be in the "Superuser" or "Technician" group.

    Attributes:
        model (Item): The model that this view will operate on.
        template_name (str): The name of the template that the view will render.
        success_url (str): The URL to redirect to upon successful deletion.
        fail_url (str): The URL to redirect to if the deletion is cancelled.

    Methods:
        test_func(): Checks if the user is in the "Superuser" or "Technician" group.
        post(request): Handles POST requests to delete the item or cancel the deletion.
    """

    model = Item
    template_name = "inventory/item_confirm_delete.html"
    success_url = reverse_lazy("inventory:items")

    def get_fail_url(self):
        """
        Returns the URL to redirect to if the deletion is canceled.

        Returns:
            str: The URL to redirect to.
        """
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
        user_group = self.request.user.groups.first()
        user_group_name = user_group.name
        return user_group != None and user_group_name in ["Superuser", "Technician"]

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to delete the item or cancel the deletion.

        Args:
            request (HttpRequest): The HTTP request object containing metadata about the request.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: The HTTP response object.
        """
        if "Cancel" in request.POST:
            url = self.fail_url
            return redirect(url)
        else:
            try:
                return super(ItemDeleteView, self).post(request, *args, **kwargs)
            except IntegrityError as e:
                messages.error(
                    request,
                    f"Cannot delete this item because it is referenced by other records: {e}",
                )
                return redirect(self.fail_url)


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
    template_name = "search/item_search.html"
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


class ImportItemDataView(UserPassesTestMixin, FormView):
    """
    Renders a view to allow users to import items from an .xlsx file to the database.

    Attributes:
        form_class (Form): The form that the view operates on.
        template_name (str): The name of the template to be rendered by the class.

    Methods:
        test_func(): Checks if the user is in the "Superuser" or "Technician" group.
        form_valid(form): Processes data from an uploaded Excel file to the database.
    """

    form_class = ImportFileForm
    template_name = "import_item_data.html"
    success_url = reverse_lazy("inventory:items")

    def test_func(self) -> bool:
        """
        Checks if the user is in the "Superuser" or "Technician" group.

        Returns:
            bool: True if the user is in the "Superuser" or "Technician" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name in ["Superuser", "Technician"]

    def form_valid(self, form) -> HttpResponseRedirect:
        """
        Processes the uploaded Excel file from the form, extracts item data from each row,
        and creates Item objects in the database.
        Empty cells will have a default value set for them in the database.

        Args:
            form (Form): The form containing the uploaded Excel file.

        Returns:
            HttpResponseRedirect: THe HTTP response to redirect to the items list view after processing the file.
        """
        file = form.cleaned_data["file"]
        workbook = load_workbook(file)
        sheet = workbook.active
        user = self.request.user

        # For each record in the excel file ...
        for row in sheet.iter_rows(min_row=2, values_only=True):
            # If the row is completely blank, stop the for loop
            if all(cell is None for cell in row):
                break

            # If not...
            # Get its data. Set to default value if None
            manufacturer = row[0] if row[0] is not None else "N/A"
            model = row[1] if row[1] is not None else "N/A"
            part_or_unit = row[2] if row[2] is not None else "Part"
            part_number = row[3] if row[3] is not None else ""
            description = (
                row[4]
                if row[4] is not None
                else ""  # str(model) + " " + str(part_number)
            )
            location = row[5] if row[5] is not None else "N/A"
            quantity = row[6] if row[6] is not None else 0
            min_quantity = row[7] if row[7] is not None else 0
            unit_price = row[8] if row[8] is not None else 0.01

            # Create a new Item with the data
            item = Item.objects.create(
                manufacturer=manufacturer,
                model=model,
                part_or_unit=part_or_unit,
                part_number=part_number,
                description=description,
                location=location,
                quantity=quantity,
                min_quantity=min_quantity,
                unit_price=unit_price,
                last_modified_by=user,
            )

            # # Create an ItemHistory record for the new item
            # ItemHistory.objects.create(
            #     item=item,
            #     action="create",
            #     user=user,
            #     changes=f"Item imported by {user.username}",
            # )

        # Go to items page after finishing
        return HttpResponseRedirect(reverse("inventory:items"))

    def save(self, *args, **kwargs):
        """
        Saves the item with additional keyword arguments.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: The HTTP response object.
        """
        kwargs["user"] = self.request.user
        return super().save(*args, **kwargs)


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
        test_func(): Checks if the user belongs to the "Technician" or "Superuser" group.
        get_queryset(): Returns the queryset of all item requests.
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
        Retrieves all Item Requests from the database.

        Returns:
            QuerySet: The queryset containing all item requests.
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

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The context data with the specific item added.
        """
        context = super().get_context_data(**kwargs)
        item_id = self.kwargs.get("pk")
        context["item"] = Item.objects.get(pk=item_id)
        return context


##############################
# Views for the UsedItem Model
##############################
class UsedItemView(LoginRequiredMixin, ListView):
    # TODO: Doc comment
    model = UsedItem
    template_name = "used_items.html"
    context_object_name = "used_items_list"

    def get_queryset(self):
        """
        Retrieves all used items from the database.

        Used items are ordered by `work_order` and then `item`.

        Returns:
            QuerySet: A queryset containing all used items.
        """
        return UsedItem.objects.all().order_by("work_order", "item")


class UsedItemDetailView(LoginRequiredMixin, DetailView):
    # TODO: Doc comment
    """
    _summary_

    Arguments:
        LoginRequiredMixin -- _description_
        DetailView -- _description_

    Returns:
        _description_
    """
    model = UsedItem
    template_name = "used_item_detail.html"

    def get_context_data(self, **kwargs):
        """
        Adds the specific used item to the context data.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The context data with the specific item that will be used by the template
        """
        context = super().get_context_data(**kwargs)
        context["used_item"] = self.object
        return context


class UsedItemCreateView(UserPassesTestMixin, CreateView):
    # TODO: Doc comment
    model = UsedItem
    # form_class = UsedItemForm
    template_name = "item_use_form.html"
    fields = "__all__"

    def test_func(self) -> bool:
        """
        Checks if the user belongs to the "Superuser" or "Technician" group.

        Returns:
            bool: True if the user is in the "Superuser" or "Technician" group, False otherwise.
        """
        user_group = self.request.user.groups.first()
        return user_group is not None and user_group.name in ["Superuser", "Technician"]

    def get_initial(self):
        initial = super().get_initial()
        item_id = self.request.GET.get("item_id")
        if item_id:
            item = get_object_or_404(Item, pk=item_id)
            initial.update(
                {
                    "item": item,
                }
            )
        return initial

    def get_context_data(self, **kwargs):
        """


        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The context data with the specific item added.
        """
        context = super().get_context_data(**kwargs)
        item_id = self.request.GET.get("item_id")
        item = Item.objects.get(pk=item_id)
        context["item"] = item
        if self.request.method == "GET":
            form = context["form"]
            form.initial.update(self.get_initial())
        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Checks if the item's quantity is greater than 0 before allowing access to the view.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponse: The HTTP response object.
        """
        item_id = self.request.GET.get("item_id")
        item = Item.objects.get(pk=item_id)
        if item.quantity <= 0:
            messages.error(request, "Cannot use item with quantity 0.")
            return redirect("inventory:item_detail", pk=item_id)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # TODO: form variable type
        """
        Override form_valid to decrement the quantity of the associated Item when a new UsedItem is created.
        It also makes an ItemHistory record to explain the decrement. 

        Args:
            form (): The form that handles the data for creating a new UsedItem object.

        Returns:
            HttpResponse: The HTTP response object
        """
        response = super().form_valid(form)
        used_item = form.instance
        item = used_item.item
        item.quantity -= 1
        item.save()

        ItemHistory.objects.create(
            item=item,
            action="use",
            user=self.request.user,
            changes=f"Item used in work order {used_item.work_order}",
        )

        return response


class SearchUsedItemsView(LoginRequiredMixin, ListView):
    """
    Class-based view for searching used items.
    This view uses Haystack to perform the search.

    Attributes:
        model (UsedItem): The model that this view will operate on.
        template_name (str): The template used to render the search results.
        context_object_name (str): The name of the context variable to use for the search results.

    Methods:
        get_queryset(): Retrieves the search results based on the query.
    """

    model = UsedItem
    template_name = "search/used_item_search.html"
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
            .models(UsedItem)
            .filter(content=query)
            .order_by("work_order", "item")
            if query
            else []
        )
        return results


#######################################
# Views for the PurchaseOrderItem model
#######################################
class PurchaseOrderItemsFormView(UserPassesTestMixin, FormView):
    """
    Renders a view to allow users to create purchase orders using a formset.

    Attributes:
        form_class (FormSet): The formset class to use for the purchase order items.
        template_name (str): The template used to render the formset.
        success_url (str): The URL to redirect to upon successful form submission.

    Methods:
        test_func(): Checks if the user is in the 'Superuser' group.
        get_context_data(**kwargs): Adds the formset to the context data.
        form_valid(formset): Processes the formset data and writes it to an Excel file for download.
    """

    form_class = PurchaseOrderItemFormSet
    template_name = "purchase_order_form.html"
    success_url = reverse_lazy("inventory:items")

    def test_func(self) -> bool:
        """
        Checks if the user is in the 'Superuser' group.

        Returns:
            bool: True if the user is in the 'Superuser' group, False otherwise.
        """
        return self.request.user.groups.first().name == "Superuser"

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.

        Returns:
            dict: The initial data for the form.
        """
        initial = super().get_initial()
        initial.update(
            {
                "manufacturer": self.request.GET.get("manufacturer", ""),
                "model_part_num": self.request.GET.get("model_part_num", ""),
                "description": self.request.GET.get("description", ""),
            }
        )
        return initial

    def get_context_data(self, **kwargs):
        """
        Adds the formset and query parameters to the context data.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The context data with the formset and query parameters added.
        """
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = PurchaseOrderItemFormSet(self.request.POST)
        else:
            context["formset"] = PurchaseOrderItemFormSet(
                queryset=PurchaseOrderItem.objects.none()
            )
        context["manufacturer"] = self.request.GET.get("manufacturer", "")
        context["model_part_num"] = self.request.GET.get("model_part_num", "")
        context["description"] = self.request.GET.get("description", "")
        return context

    def form_valid(self, formset):
        """
        Processes the formset data and writes it to an Excel file for download.

        This method is called when valid form data has been POSTed. It writes the purchase order data
        from the formset to an Excel file using a predefined template and returns an HTTP response
        to download the generated Excel file.

        Args:
            formset (FormSet): The formset containing the purchase order data.

        Returns:
            HttpResponse: The HTTP response object to download the Excel file.
        """
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            'attachment; filename="new_purchase_order.xlsx"'
        )
        po_template_path = "PO_Template.xlsx"
        workbook = load_workbook(po_template_path)
        worksheet = workbook.active

        # Setup function if there are 8 or more items.
        itemCount = 0

        for form in formset:
            itemCount += 1

        if itemCount >= 8:
            setup_worksheet(worksheet, itemCount)

        # workbook.save()

        # Write data to the worksheet
        row = 16
        for form in formset:
            if form.cleaned_data.get("DELETE"):
                continue

            manufacturer = form.cleaned_data["manufacturer"]
            model_part_num = form.cleaned_data["model_part_num"]
            quantity_ordered = form.cleaned_data["quantity_ordered"]
            description = form.cleaned_data["description"]
            serial_num = form.cleaned_data["serial_num"]
            property_num = form.cleaned_data["property_num"]
            unit_price = form.cleaned_data["unit_price"]

            worksheet[f"B{row}"] = manufacturer
            worksheet[f"C{row}"] = model_part_num
            worksheet[f"D{row}"] = quantity_ordered
            worksheet[f"E{row}"] = description
            worksheet[f"G{row}"] = serial_num
            worksheet[f"H{row}"] = property_num
            worksheet[f"I{row}"] = unit_price
            row += 1

        # Apply custom number format to the last row
        worksheet[f"I{row-1}"].number_format = (
            "_($* #,##0.00_);_($* (#,##0.00);_($* -_0_0_);_(@"
        )
        worksheet[f"J{row-1}"].number_format = (
            "_($* #,##0.00_);_($* (#,##0.00);_($* -_0_0_);_(@"
        )

        # Save the workbook content to the response object
        workbook.save(response)

        return response
