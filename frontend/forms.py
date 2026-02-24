from django import forms
from django.forms import ModelForm
import logging

logger = logging.getLogger(__name__)


class FrontendModelForm(ModelForm):
    """
    A class representing a Django ModelForm with default configurations for frontend usage.

    :inherit: ModelForm from django.forms
    """

    class Meta:
        """
        A class representing a Django ModelForm with default configurations for frontend usage.

        :inherit: ModelForm from django.forms
        """

        model = None
        fields = ()

def generate_form_for_model(model, fields):
    """
    Generate a Django ModelForm class for the given model and fields.

    :param model: The Django model to generate the form for
    :param fields: The fields to be included in the form.
                   An empty/falsy value results in an empty tuple — never "__all__".
    :return: A dynamically created ModelForm class for the given model and fields
    """

    if not fields:
        logger.warning(
            "generate_form_for_model called for %s without explicit fields. "
            "Defaulting to empty field list. Set 'fields' or 'list_display' on "
            "your ModelFrontend to specify which fields to expose.",
            model.__name__,
        )
        fields = ()
    Meta = type("Meta", (), {"model": model, "fields": fields})
    form_class = type(f"{model.__name__}Form", (ModelForm,), {"Meta": Meta})
    return form_class
