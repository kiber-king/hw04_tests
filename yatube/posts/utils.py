from django.core.paginator import Paginator

LATEST_POSTS_COUNT = 10


def get_paginator(request, obj_list):
    paginator = Paginator(obj_list, LATEST_POSTS_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
