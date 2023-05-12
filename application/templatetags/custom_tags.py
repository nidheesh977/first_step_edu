from django import template
from application.models import Classes, CompetitiveExam

register = template.Library()


@register.simple_tag
def get_five_class_exams():
     class_exams = Classes.objects.all().order_by("-purchase_count")[:5]
     return class_exams

@register.simple_tag
def get_five_competitive_exams():
     competitive_exams = CompetitiveExam.objects.all().order_by("-purchase_count")[:5]
     return competitive_exams

@register.simple_tag
def space_replace(value):
      return str(value).replace(" ","%20")

@register.filter
def subtract(value, arg):
    return value - arg
