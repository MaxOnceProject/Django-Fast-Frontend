from django.core.paginator import Paginator
from django.db.models import Q
from frontend.forms import generate_form_for_model
from .abstract import FrontendAbstract
from .mixin import NotImplementedMixin


class ModelFrontend(FrontendAbstract, NotImplementedMixin):
    """
    A class representing a frontend configuration for a Django model.

    :param model: The Django model to configure frontend settings for
    """

    # login
    login_required = True

    # toolbar
    toolbar_button = tuple()
    description = str()

    # table
    list_display = tuple()
    cards = False
    list_per_page = 100
    view_permission = True
    inline_button = tuple()

    # table search, sort and filter
    search_fields = tuple()
    sortable_by = tuple()  # List of fields available for sorting
    list_filter = tuple()  # List of fields available for filtering

    # form
    fields = list_display  # follows list_display by default
    readonly_fields = tuple()
    change_permission = False
    delete_permission = False
    add_permission = False

    def __init__(self, *args, **kwargs):
        self.model = kwargs.get('model', None)

    def get_urls(self, site):
        return site.urls()

    def get_readonly_fields(self):
        return self.readonly_fields

    def get_list_display(self):
        return self.list_display

    def get_fields(self):
        return self.fields

    def get_search_fields(self):
        return self.search_fields

    def get_list_filter(self):
        return self.list_filter

    def get_sortable_by(self):
        return self.sortable_by

    def get_list_per_page(self):
        return self.list_per_page

    def has_view_permission(self):
        return self.view_permission

    def has_add_permission(self):
        return self.add_permission

    def has_change_permission(self):
        return self.change_permission

    def has_delete_permission(self):
        return self.delete_permission

    def get_login_required(self):
        return self.login_required

    def get_toolbar_button(self):
        return self.toolbar_button

    def get_cards(self):
        return self.cards
    def get_inline_button(self):
        return self.inline_button

    def get_form(self):
        """
        Redirects the user to the login page with the current path as the next URL.
        """

        fields = self.get_fields()

        return generate_form_for_model(self.model, fields)

    def queryset(self, *args, **kwargs):
        """
        gets objects of a model with the specified fields.
        """

        qs = self.model._default_manager.get_queryset()
        fields = self.get_fields()

        if 'id' in fields:
            objects = qs.values(*fields)
        elif not fields:
            objects = qs.values()
            if objects.exists():
                fields = [field for field in objects[0].keys() if field != 'id']
            else:
                fields = [field.name for field in self.model._meta.fields if field.name != 'id']
        else:
            objects = qs.values(*fields, 'id')
        return objects, list(fields)

    def get_pagination(self, request, objects):
        """
        gets a paginator for the objects and returns the paginated objects.
        """

        list_per_page = self.get_list_per_page()

        paginator = Paginator(objects, list_per_page)  # Show x items per page
        objects = paginator.get_page(request.GET.get("page"))
        return objects

    def get_model_actions(self, inline_button):
        table_fields = []
        if inline_button:
            for action in inline_button:
                table_fields += [action]
        return list(table_fields)

    def get_search_results(self, objects, search_fields, search_query):
        # Apply search filters
        if search_fields and search_query:
            query = Q()
            for field in search_fields:
                query |= Q(**{f"{field}__icontains": search_query})
            objects = objects.filter(query)
        return objects

    def get_filter_results(self, objects, filter_fields, filter_args):
        # Apply additional filters from filter_params
        if filter_fields and filter_args:
            query = Q()
            for field in filter_fields:
                if field in filter_args:
                    # query &= Q(**{f"{field}__in": filter_args[field]})
                    for filter_arg in filter_args[field]:
                        query |= Q(**{f"{field}__icontains": filter_arg})
            objects = objects.filter(query)
        return objects

    def get_sort_results(self, objects, sort_fields, sort_args):
        # Apply sorting from sort_params
        if sort_fields and sort_args:
            sort_fields = list(sort_fields) + [f'-{field}' for field in sort_fields]
            if sort_args and sort_args in sort_fields:
                objects = objects.order_by(sort_args)

        return objects

    def get_filter_options(self):
        list_filter = self.get_list_filter()
        filter_options = {}
        for field in list_filter:
            filter_field = self.model._meta.get_field(field)
            filter_options[field] = filter_field.choices if hasattr(filter_field, 'choices') and filter_field.choices else self.model.objects.values_list(field, flat=True).distinct()
        return filter_options

    def get_filter_args(self, request_get):
        request_dict = dict(request_get)
        filter_args = {filter: request_dict[filter] for filter in request_dict if filter not in ['q', 's'] and request_get[filter] != ''}
        return filter_args
