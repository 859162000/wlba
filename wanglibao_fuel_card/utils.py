#!/usr/bin/env python
# encoding: utf-8


def get_sorts_for_created_time(self, queryset, reverse=True):
    """根据 created_time 对请求集排序（reverse=True降序, False升序）"""

    data_list = sorted(queryset, key=lambda asd: asd.created_time, reverse=reverse)

    return data_list