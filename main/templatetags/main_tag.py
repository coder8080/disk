from django import template

register = template.Library()


@register.inclusion_tag('main/tags/header.html')
def get_header(page="main"):
    return {"page": page}
