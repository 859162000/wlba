# encoding: utf-8

import random
import datetime
from django.db import transaction
from weixin.util import getMiscValue
from weixin.models import WeixinUser
from .models import WechatUserDailyReward, InviteRelation, UserExtraInfo
from wanglibao_redpack.backends import give_activity_redpack_for_hby, _send_message_for_hby, get_start_end_time
from wanglibao_redpack.models import RedPackEvent
from experience_gold.backends import SendExperienceGold
from wanglibao_p2p.models import P2PRecord

def iter_method(data):
    total = sum([vv[1] for vv in data.values()])
    rad = random.randint(1,total)

    cur_total = 0
    res = ""
    for k, v in data.items():
        cur_total += v[1]
        if rad<= cur_total:
            res = k
            break
    return res

def getRandomRedpackId(redpack_data):
    # redpack_data = {'1': [0, 20], '2': [0, 30], '3': [0, 40], '4': [0, 10]}
    redpack_id = iter_method(redpack_data)
    return redpack_id

def getWechatDailyReward(openid):
    w_user = WeixinUser.objects.get(openid=openid)
    today = datetime.datetime.today()
    share_invite_config = getMiscValue("redpack_rain_award_config")
    # {"reward_types":["redpack", "experience_gold"], "daily_rewards":{'371': [0,20],'372': [0,30], '373': [0,40], '374': [0,10]},
    # "new_old_map":{"371":380,"372":381,"373":382,"374":383},"base_experience_amount":200000}
    redpack_data = {'1': [0, 20], '2': [0, 30], '3': [0, 40], '4': [0, 10]}# share_invite_config["daily_rewards"]
    reward_types = share_invite_config['reward_types']
    redpack_id = getRandomRedpackId(redpack_data)
    redpack_type = reward_types[redpack_data[redpack_id][0]]
    daily_reward, _ = WechatUserDailyReward.objects.get_or_create(
        create_date=today,
        w_user=w_user,
        reward_type=redpack_type,#pei zhi
        # action_type="redpack_rain",#pei zhi
        redpack_id=int(redpack_id),
    )
    if daily_reward.status:
        return -1, ""
    user = w_user.user
    if not user:
        return -1, ""
    return sendDailyReward(user, daily_reward.id, save_point=True)


def sendDailyReward(user, daily_reward_id, save_point=False, new_registed=False):
    with transaction.atomic(savepoint=save_point):
        daily_reward = WechatUserDailyReward.objects.select_for_update().get(id=daily_reward_id)
        if daily_reward.status:
            return -1, ""
        if daily_reward.reward_type == "redpack":
            share_invite_config = getMiscValue("redpack_rain_award_config")
            # {"reward_types":["redpack", "experience_gold"], "daily_rewards":{'371': [0,20],'372': [0,30], '373': [0,40], '374': [0,10]},
            # "new_old_map":{"371":380,"372":381,"373":382,"374":383},"base_experience_amount":200000}
            new_old_map = share_invite_config.get("new_old_map", {})
            if not new_registed:
                #如果是老用户，发放misc里面配置的与新用户红包等额的老用户红包
                real_redpack_id = int(new_old_map.get(str(daily_reward.redpack_id), daily_reward.redpack_id))
                daily_reward.redpack_id = real_redpack_id

            redpack_event = RedPackEvent.objects.get(id=daily_reward.redpack_id)
            status, msg, record = give_activity_redpack_for_hby(user, redpack_event, 'h5')
            if not status:
                return -1, msg

            start_time, end_time = get_start_end_time(redpack_event.auto_extension, redpack_event.auto_extension_days,
                                                          record.created_at, redpack_event.available_at, redpack_event.unavailable_at)
            _send_message_for_hby(user, redpack_event, end_time)
            daily_reward.redpack_record_id = record.id
        if daily_reward.reward_type == "experience_gold":
            experience_record_id, experience_event = SendExperienceGold(user).send(pk=daily_reward.experience_gold_id)
            if not experience_record_id:
                return -1, ""
            daily_reward.experience_gold_record_id = experience_record_id
        daily_reward.user = user
        daily_reward.status = True
        daily_reward.save()
        return 0, "ok"

# def sendInviteReward(user):
#     # {"reward_types":["redpack", "experience_gold"], "daily_rewards":{'1': [0,20],'2': [0,30], '3': [0,40], '4': [0,10]}
#     # "first_invest":1000, "base_experience_amount":200000, "first_invest_reward":1, "first_invest_reward_type":0, "invite_experience_id":1}
#     share_invite_config = getMiscValue("share_invite_config")
#     base_experience_amount = share_invite_config.get('base_experience_amount', 0)
#     # InviteRewardRecord
#     inv_relation = InviteRelation.objects.filter(user=user).first()
#     if inv_relation:
#         inviter = inv_relation.inviter
#         if inviter:
#             inviter_extra = UserExtraInfo.objects.filter(user=inviter).first()
#             if inviter_extra.invite_experience_amount < base_experience_amount:
#                 #todo
#                 invite_experience_id = share_invite_config['invite_experience_id']
#                 SendExperienceGold(user).send(pk=invite_experience_id)
#
# def sendInvestReward(user):
#     # {"reward_types":["redpack", "experience_gold"], "daily_rewards":{'1': [0,20],'2': [0,30], '3': [0,40], '4': [0,10]}
#     # "first_invest":1000, "base_experience_amount":200000, "first_invest_reward":1, "first_invest_reward_type":0, "invite_experience_id":1}
#     share_invite_config = getMiscValue("share_invite_config")
#     # InviteRewardRecord
#     inv_relation = InviteRelation.objects.filter(user=user).first()
#     if inv_relation:
#         inviter = inv_relation.inviter
#         if inviter:
#             first_buy = P2PRecord.objects.filter(user=user,
#                                                  # create_time__gt=
#                                                  ).order_by('create_time').first()


# [2016-04-14 15:08:56,293: INFO/MainProcess] Task weixin.tasks.bind_ok[22a2c590-55c5-437a-a647-2ba7c2dcaeeb] succeeded in 0.153715637s: None
# [2016-04-14 15:08:56,344: ERROR/MainProcess] Task wanglibao_invite.tasks.processShareInviteDailyReward[8388bdaa-033e-4ebb-ae25-a8e607ace6a8] raised unexpected: TypeError("'int' object has no attribute '__getitem__'",)
# Traceback (most recent call last):
#   File "/usr/local/lib/python2.7/dist-packages/celery/app/trace.py", line 240, in trace_task
#     R = retval = fun(*args, **kwargs)
#   File "/usr/local/lib/python2.7/dist-packages/celery/app/trace.py", line 437, in __protected_call__
#     return self.run(*args, **kwargs)
#   File "/home/wanglibao-dev/wangli-backend/wanglibao-backend/wanglibao_invite/tasks.py", line 13, in processShareInviteDailyReward
#     user = User.objects.get(user_id)
#   File "/usr/local/lib/python2.7/dist-packages/django/db/models/manager.py", line 151, in get
#     return self.get_queryset().get(*args, **kwargs)
#   File "/usr/local/lib/python2.7/dist-packages/django/db/models/query.py", line 301, in get
#     clone = self.filter(*args, **kwargs)
#   File "/usr/local/lib/python2.7/dist-packages/django/db/models/query.py", line 593, in filter
#     return self._filter_or_exclude(False, *args, **kwargs)
#   File "/usr/local/lib/python2.7/dist-packages/django/db/models/query.py", line 611, in _filter_or_exclude
#     clone.query.add_q(Q(*args, **kwargs))
#   File "/usr/local/lib/python2.7/dist-packages/django/db/models/sql/query.py", line 1198, in add_q
#     if not self.need_having(q_object):
#   File "/usr/local/lib/python2.7/dist-packages/django/db/models/sql/query.py", line 1161, in need_having
#     return any(self.need_having(c) for c in obj.children)
#   File "/usr/local/lib/python2.7/dist-packages/django/db/models/sql/query.py", line 1161, in <genexpr>
#     return any(self.need_having(c) for c in obj.children)
#   File "/usr/local/lib/python2.7/dist-packages/django/db/models/sql/query.py", line 1158, in need_having
#     return (refs_aggregate(obj[0].split(LOOKUP_SEP), self.aggregates)
# TypeError: 'int' object has no attribute '__getitem__'
