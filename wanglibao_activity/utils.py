# -*- coding: utf-8 -*-

from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger


def get_queryset_paginator(queryset, page, pagesize):
    data_list = []
    data_list.extend(queryset)

    paginator = Paginator(data_list, pagesize)

    try:
        data_list = paginator.page(page)
    except PageNotAnInteger:
        data_list = paginator.page(1)
    except Exception:
        data_list = paginator.page(paginator.num_pages)

    return data_list, paginator.num_pages, paginator.count
