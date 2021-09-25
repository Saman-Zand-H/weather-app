from django import template

register = template.Library()

@register.filter(name="add_days")
def add_days(delta, date):
    return delta + date

@register.filter(name="get_item")
def get_item(dict, key):
    return dict.get(key)