#!/usr/bin/env python
# encoding: utf-8

from marketing.models import RevenueExchangeRule


def get_sorts_for_created_time(queryset, reverse=True):
    """根据 created_time 对请求集排序（reverse=True降序, False升序）"""

    data_list = sorted(queryset, key=lambda asd: asd.created_time, reverse=reverse)

    return data_list


def get_p2p_reward_using_range(l_type):
    """获取p2p奖品使用范围"""

    return RevenueExchangeRule.REWARD_RANGE_DESCRIPTION.get(l_type, '')
