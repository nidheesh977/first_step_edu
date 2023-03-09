from django import template

register = template.Library()

@register.simple_tag
def space_replace(value):
      return str(value).replace(" ","%20")

@register.filter
def subtract(value, arg):
    return value - arg