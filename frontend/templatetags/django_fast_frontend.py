# your_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def split(value, arg):
    return value.split(arg)


@register.filter()
def label(value):
    value = value.replace('_', ' ')
    return value.title()