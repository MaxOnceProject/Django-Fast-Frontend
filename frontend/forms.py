from django import forms
from django.forms import ModelForm

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
        fields = "__all__"

def generate_form_for_model(model, fields):
    """
    Generate a Django ModelForm class for the given model and fields.

    :param model: The Django model to generate the form for
    :param fields: The fields to be included in the form
    :return: A dynamically created ModelForm class for the given model and fields
    """

    if not fields:
        fields = "__all__"
    Meta = type("Meta", (), {"model": model, "fields": fields})
    form_class = type(f"{model.__name__}Form", (ModelForm,), {"Meta": Meta})
    return form_class
