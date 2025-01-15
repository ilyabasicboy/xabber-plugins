from django import template
from django.core.paginator import Paginator, EmptyPage

from xabber_plugins.utils import get_success_messages, get_error_messages

register = template.Library()


@register.simple_tag(takes_context=True)
def paginate(context, objects, num=10):
    request = context.get('request')

    try:
        page = int(request.GET.get('page'))
    except:
        page = 1

    paginator = Paginator(objects, num)

    try:
        objects = paginator.page(page)
    except EmptyPage:
        # If the page is out of range (e.g., 9999), deliver the last page of results
        objects = paginator.page(paginator.num_pages)

    return objects


@register.simple_tag(takes_context=True)
def get_messages(context):
    messages = {}
    request = context.get('request')
    if request:
        success_messages = get_success_messages(request)
        if success_messages:
            messages['success'] = success_messages

        error_messages = get_error_messages(request)
        if error_messages:
            messages['error'] = error_messages

    return messages