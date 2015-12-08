# -*- coding: utf-8 -*-

from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
import re


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


def get_activity_show_status_num(activity_show):
    activity_status = activity_show.activity_status()
    # activity_status = activity_status.encode('utf-8')
    if activity_status == u'进行中':
        return 'c'

    if activity_status == u'未开始':
        return 'd'

    if activity_status == u'已结束':
        return 'e'

    match = re.findall(ur'(?<=剩)\d+(?=小时)', activity_status)
    if match:
        return 'a%s' % int(match[0])

    match = re.findall(ur'(?<=剩)\d+(?=天)', activity_status)
    if match:
        return 'b%s' % int(match[0])

    return 'e'


def get_sorts_for_activity_show(queryset):
    activity_list = []
    for q in queryset:
        index = get_activity_show_status_num(q)
        activity_list.append((index, q))

    activity_list = sorted(activity_list, key=lambda asd:asd[0], reverse=False)
    activity_list = (q[1] for q in activity_list)

    return activity_list
