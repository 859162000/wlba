#!/usr/bin/env python
# encoding: utf-8

from marketing.models import P2PReward
from marketing.utils import get_user_channel_record


def get_sorts_for_created_time(queryset, reverse=True):
    """根据 created_time 对请求集排序（reverse=True降序, False升序）"""

    data_list = sorted(queryset, key=lambda asd: asd.created_time, reverse=reverse)

    return data_list


def get_p2p_reward_using_range(user_id, _type, price):
    """获取p2p奖品使用范围"""

    channel = get_user_channel_record(user_id)
    if channel:
        using_range = P2PReward.objects.values('using_range').filter(channel=channel,
                                                                     type=_type, is_used=False,
                                                                     price=price).first().distinct()

        return (ur['using_range'] for ur in using_range)
