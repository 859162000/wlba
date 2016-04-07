# encoding: utf-8

import random
import datetime
from django.db import transaction
from weixin.util import getMiscValue
from weixin.models import WeixinUser
from .models import WechatUserDailyReward, InviteRelation, InviteRewardRecord, UserExtraInfo
from wanglibao_redpack.backends import give_activity_redpack_for_hby, _send_message_for_hby, get_start_end_time
from wanglibao_redpack.models import RedPackEvent
from experience_gold.backends import SendExperienceGold


def iter_method(data):
    total = sum(data.values())
    rad = random.randint(1,total)

    cur_total = 0
    res = ""
    for k, v in data.items():
        cur_total += v
        if rad<= cur_total:
            res = k
            break
    return res

def getRandomRedpackId():
    # redpack_data = getMiscValue("redpack_rain")
    redpack_data = {'1': 20,'2': 30, '3': 40, '4': 10}
    redpack_id = int(iter_method(redpack_data))
    return redpack_id

def getWechatDailyReward(openid):
    w_user = WeixinUser.objects.get(openid=openid)
    today = datetime.datetime.today()
    redpack_id = getRandomRedpackId()
    daily_reward, _ = WechatUserDailyReward.objects.get_or_create(
        create_date=today,
        w_user=w_user,
        reward_type='redpack',#pei zhi
        action_type="redpack_rain",#pei zhi
        redpack_id=redpack_id,
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

def sendInviteReward(user):
    InviteRewardRecord
    inv_relation = InviteRelation.objects.filter(user=user).first()
    if inv_relation:
        inviter = inv_relation.inviter
        if inviter:
            inviter_extra = UserExtraInfo.objects.filter(user=inviter).first()
            if inviter_extra.invite_experience_amount > 20000:
                #todo
                #give redpack
                pass







