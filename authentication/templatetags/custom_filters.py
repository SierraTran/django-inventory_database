from django import template

register = template.Library()

@register.filter(name="clean_id_for_label")
def clean_id_for_label(value):
    return value.replace("id_", "")