"""Паджинатор для views.py"""
from django.core.paginator import Paginator
from django.conf import settings


def paginator_obg(request, post):
    paginator = Paginator(post, settings.PAGE_COUNTER_TEN)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
