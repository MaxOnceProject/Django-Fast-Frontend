from django.contrib.admin.utils import display_for_field
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.text import capfirst
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

    def get_form_fields(self):
        fields = self.get_fields()
        if not fields:
            return fields
        return tuple(
            field_name
            for field_name in fields
            if self.model._meta.get_field(field_name).editable
        )

    def get_non_editable_fields(self):
        fields = self.get_fields()
        if not fields:
            return tuple()
        return tuple(
            field_name
            for field_name in fields
            if not self.model._meta.get_field(field_name).editable
        )

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

    @staticmethod
    def _default_action_label(name):
        return name.replace('_', ' ').title()

    def _format_action_description(self, description):
        if not self.model:
            return description

        opts = self.model._meta
        try:
            return description % {
                'verbose_name': opts.verbose_name,
                'verbose_name_plural': opts.verbose_name_plural,
            }
        except (KeyError, TypeError, ValueError):
            return description

    def get_action_label(self, action_name):
        handler = getattr(self, action_name, None)
        description = getattr(handler, 'short_description', None)
        if description is None and hasattr(handler, '__func__'):
            description = getattr(handler.__func__, 'short_description', None)
        if description:
            return self._format_action_description(description)
        return self._default_action_label(action_name)

    def get_action_definition(self, action_name):
        return {
            'name': action_name,
            'label': self.get_action_label(action_name),
        }

    def get_toolbar_actions(self):
        return [self.get_action_definition(action_name) for action_name in self.get_toolbar_button()]

    def get_cards(self):
        return self.cards

    def get_inline_button(self):
        return self.inline_button

    def get_inline_actions(self):
        return [self.get_action_definition(action_name) for action_name in self.get_inline_button()]

    def get_readonly_field_value(self, obj, field_name, empty_value_display='-'):
        field = self.model._meta.get_field(field_name)
        value = field.value_from_object(obj)
        return display_for_field(value, field, empty_value_display)

    def get_form_layout(self, form=None, obj=None):
        form_layout = []
        readonly_fields = set(self.get_non_editable_fields())

        for field_name in self.get_fields():
            if form is not None and field_name in form.fields:
                form_layout.append({
                    'type': 'field',
                    'name': field_name,
                    'bound_field': form[field_name],
                })
                continue

            if obj is not None and field_name in readonly_fields:
                model_field = self.model._meta.get_field(field_name)
                form_layout.append({
                    'type': 'readonly',
                    'name': field_name,
                    'label': capfirst(model_field.verbose_name),
                    'value': self.get_readonly_field_value(obj, field_name),
                })

        return form_layout

    def get_form(self):
        """
        Redirects the user to the login page with the current path as the next URL.
        """

        fields = self.get_form_fields()

        return generate_form_for_model(self.model, fields)

    def get_queryset(self, request=None):
        """
        Returns the base queryset for this model, optionally scoped by the
        current request/user.  Override in subclasses to implement row-level
        authorization (e.g. filter by request.user).

        :param request: The current Django HttpRequest (optional for backward compat)
        :return: A Django QuerySet
        """
        return self.model._default_manager.get_queryset()

    def queryset(self, request=None, *args, **kwargs):
        """
        Gets objects of a model with the specified fields.
        Delegates to get_queryset(request) so subclass overrides are respected.
        """

        qs = self.get_queryset(request)
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

        if hasattr(objects, 'ordered') and not objects.ordered:
            objects = objects.order_by('pk')
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
