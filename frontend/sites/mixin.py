class NotImplementedMixin:

    @property
    def actions(self):
        raise NotImplementedError('Use option table_inline_button or toolbar_button.')

    @property
    def actions_on_top(self):
        return NotImplementedError('Use option table_inline_button or toolbar_button.')

    @property
    def actions_on_bottom(self):
        return NotImplementedError('Use option table_inline_button or toolbar_button.')

    @property
    def empty_value_display(self):
        raise NotImplementedError

    @property
    def ordering(self):
        raise NotImplementedError('Use option sortable_by.')

    @property
    def preserve_filters(self):
        raise NotImplementedError

    @property
    def search_help_text(self):
        raise NotImplementedError

    @property
    def show_full_result_count(self):
        raise NotImplementedError

    @property
    def form(self):
        raise NotImplementedError

    @property
    def autocomplete_fields(self):
        raise NotImplementedError

    @property
    def list_select_related(self):
        raise NotImplementedError

    @property
    def formfield_overrides(self):
        raise NotImplementedError

    @property
    def delete_selected_confirmation_template(self):
        raise NotImplementedError

    @property
    def delete_confirmation_template(self):
        raise NotImplementedError

    @property
    def change_list_template(self):
        raise NotImplementedError

    @property
    def change_form_template(self):
        raise NotImplementedError

    @property
    def add_form_template(self):
        raise NotImplementedError

    @property
    def actions_selection_counter(self):
        raise NotImplementedError

    @property
    def date_hierarchy(self):
        raise NotImplementedError('Use option search_fields.')

    @property
    def exclude(self):
        raise NotImplementedError('Use option fields to specify fields to display in form.')

    @property
    def fieldsets(self):
        raise NotImplementedError('Used in Django to cover complex edge case functionality.')

    @property
    def filter_horizontal(self):
        raise NotImplementedError('Use option search_fields.')

    @property
    def filter_vertical(self):
        raise NotImplementedError('Use option search_fields.')

    @property
    def inlines(self):
        raise NotImplementedError('Adding more Information to the Page will bloat the frontend.')

    @property
    def list_display_links(self):
        raise NotImplementedError('An Edit Button will be in place if editing the table row is allowed.')

    @property
    def list_editable(self):
        raise NotImplementedError('Use option readonly_fields.')

    @property
    def paginator(self):
        raise NotImplementedError('Used in Django to cover edge cases.')

    @property
    def prepopulated_fields(self):
        raise NotImplementedError('Use a custom frontend page and use java script or add a custom model form.')

    @property
    def radio_fields(self):
        raise NotImplementedError('Use a custom model form.')

    @property
    def raw_id_fields(self):
        raise NotImplementedError

    @property
    def save_as(self):
        raise NotImplementedError

    @property
    def save_as_continue(self):
        raise NotImplementedError

    @property
    def save_on_top(self):
        raise NotImplementedError

    @property
    def view_on_site(self):
        raise NotImplementedError

    def get_autocomplete_fields(self):
        raise NotImplementedError

    def save_model(self):
        raise NotImplementedError('Use a proxy model and override the save() method.')

    def save_formset(self):
        raise NotImplementedError('Use a proxy model and override the save() method.')

    def delete_model(self):
        raise NotImplementedError('Use a proxy model and override the save() method.')

    def delete_queryset(self):
        raise NotImplementedError('Use a proxy model and override the save() method.')

    def get_prepopulated_fields(self):
        raise NotImplementedError

    def get_list_display_links(self):
        raise NotImplementedError

    def get_exclude(self):
        raise NotImplementedError

    def get_fieldsets(self):
        raise NotImplementedError

    def get_inline_instances(self):
        raise NotImplementedError

    def get_inlines(self):
        raise NotImplementedError

    def get_formsets_with_inlines(self):
        raise NotImplementedError

    def formfield_for_foreignkey(self):
        raise NotImplementedError

    def formfield_for_manytomany(self):
        raise NotImplementedError

    def formfield_for_choice_field(self):
        raise NotImplementedError

    def get_changelist_formset(self):
        raise NotImplementedError

    def response_add(self):
        raise NotImplementedError

    def response_change(self):
        raise NotImplementedError

    def response_delete(self):
        raise NotImplementedError

    def get_formset_kwargs(self):
        raise NotImplementedError

    def get_deleted_objects(self):
        raise NotImplementedError

    def add_view(self):
        raise NotImplementedError

    def change_view(self):
        raise NotImplementedError

    def delete_view(self):
        raise NotImplementedError

    def get_changeform_initial_data(self):
        raise NotImplementedError

    def message_user(self):
        raise NotImplementedError

    def lookup_allowed(self):
        raise NotImplementedError

    def get_list_select_related(self):
        raise NotImplementedError

    def save_related(self):
        raise NotImplementedError

    def get_ordering(self):
        raise NotImplementedError


# class LegacyMixin:
#     url_for_result
#     check_url_mapping
#     get_queryset -> done
#     get_changelist
#     has_add_permission -> done
#     render_change_form
#     save_model
#     get_button
#     get_actions
#     add_buttons
#
#     inlines
#     inline_actions