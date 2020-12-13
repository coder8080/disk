from django import template

register = template.Library()


@register.inclusion_tag('main/tags/header.html')
def get_header(page="main", theme='light'):
    return {"page": page, "theme": theme}
