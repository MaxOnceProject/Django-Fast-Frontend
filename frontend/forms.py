from django import forms
from django.forms import ModelForm

class FrontendModelForm(ModelForm):
    class Meta:
        model = None
        fields = "__all__"

def generate_form_for_model(model, fields):
    if not fields:
        fields = "__all__"
    Meta = type("Meta", (), {"model": model, "fields": fields})
    form_class = type(f"{model.__name__}Form", (ModelForm,), {"Meta": Meta})
    return form_class
