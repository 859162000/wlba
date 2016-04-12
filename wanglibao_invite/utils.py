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
    share_invite_config = getMiscValue("share_invite_config")
    # {"reward_types":["redpack", "experience_gold"], "daily_rewards":{'1': [0,20],'2': [0,30], '3': [0,40], '4': [0,10]}
    # "first_invest":1000, "base_experience_amount":200000, "first_invest_reward":1, "first_invest_reward_type":0}
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


def sendDailyReward(user, daily_reward_id, save_point=False):
    with transaction.atomic(savepoint=save_point):
        daily_reward = WechatUserDailyReward.objects.select_for_update().get(id=daily_reward_id)
        if daily_reward.status:
            return -1, ""
        if daily_reward.reward_type == "redpack":
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








