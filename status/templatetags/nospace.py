from django import template

register = template.Library()


def nospace(value):
    return value.replace(" ","")

register.filter('nospace',nospace)