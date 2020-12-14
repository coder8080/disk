from django import template

register = template.Library()


@register.inclusion_tag('main/tags/header.html')
def get_header(page, request):
    if request.user.is_authenticated:
        return {"page": page, "theme": request.user.disk_set.all()[0].theme}
    else:
        return {'page': page, 'theme': 'light'}
