# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from wanglibao_redpack.models import RedPackRecord, RedPack


def send_redpacks(redpack_id, user_ids):
    """
    发送此红包给对应的用户
    :param redpack_id:         红包活动id
    :param user_ids:           用户list
    :return:
    """
    red_pack = RedPack.objects.filter(pk=redpack_id).first()

    users = User.objects.filter(id__in=user_ids)
    args_list = []

    for user in users:
        args_list.append(RedPackRecord(redpack=red_pack, user=user))

    try:
        RedPackRecord.objects.bulk_create(args_list)
        return {'status': 1, 'msg': 'success!'}
    except Exception, e:
        return {'status': 0, 'msg': 'send redpacks error: {}'.format(str(e))}
