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
from weixin.tasks import sentCustomerMsg
from wanglibao.templatetags.formatters import safe_phone_str

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
    redpack_data = share_invite_config["daily_rewards"]
    reward_types = share_invite_config['reward_types']
    redpack_id = getRandomRedpackId(redpack_data)
    redpack_type = reward_types[redpack_data[redpack_id][0]]
    yestoday = (datetime.datetime.now()-datetime.timedelta(days=1)).date()
    user = w_user.user
    if WechatUserDailyReward.objects.filter(create_date=today, w_user=w_user).exists():
        return -1, "微信号今天已经领取过", 0
    if user:
        if WechatUserDailyReward.objects.filter(create_date=today, user=user, status=True).exists():
            return -1, "绑定手机号今天已经领取过", 0
    else:
        if WechatUserDailyReward.objects.filter(create_date=yestoday, w_user=w_user, status=False).exists():
            return -1, "不绑定服务号只能领取一天", 0

    # if not user and WechatUserDailyReward.objects.filter(create_date=yestoday, w_user=w_user, status=False).exists():
    #     return -1, "不绑定服务号只能领取一天", 0
    # if not user and WechatUserDailyReward.objects.filter(create_date=today, w_user=w_user, status=False).exists():
    #     return -1, "微信号今天已经领取过", 0
    daily_reward, _ = WechatUserDailyReward.objects.get_or_create(
        create_date=today,
        w_user=w_user,
        defaults={
            'reward_type': redpack_type,
            'redpack_id': int(redpack_id),
        }
    )
    if daily_reward.status:
        return -1, "微信号今天已经领取过", 0
    if not user:
        return 0, "ok", 0

    return sendDailyReward(user, daily_reward.id, openid, save_point=True, isbind=False)


def sendDailyReward(user, daily_reward_id, openid, save_point=False, new_registed=False, isbind=True):
    # today = datetime.datetime.today()
    fetch_state=0
    with transaction.atomic(savepoint=save_point):
        daily_reward = WechatUserDailyReward.objects.select_for_update().get(id=daily_reward_id)
        amount = 0
        if daily_reward.status:
            return -1, "已经领取过", 0
        if WechatUserDailyReward.objects.filter(create_date=daily_reward.create_date, user=user, status=True).exists():
            daily_reward.status = True
            daily_reward.desc = "绑定发放给用户%s，但是该天用户已经领取过，所以该领奖作废"%user.id
            fetch_state = 1
        else:
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
                    return -1, msg, amount

                start_time, end_time = get_start_end_time(redpack_event.auto_extension, redpack_event.auto_extension_days,
                                                              record.created_at, redpack_event.available_at, redpack_event.unavailable_at)
                _send_message_for_hby(user, redpack_event, end_time)
                daily_reward.redpack_record_id = record.id
                amount = redpack_event.amount
            if daily_reward.reward_type == "experience_gold":
                experience_record_id, experience_event = SendExperienceGold(user).send(pk=daily_reward.experience_gold_id)
                if not experience_record_id:
                    return -1, "体验金活动不存在", amount
                daily_reward.experience_gold_record_id = experience_record_id
                amount = experience_event.amount
            if isbind:
                daily_reward.desc="绑定发放"
            else:
                daily_reward.desc="领取发放"
            fetch_state = 2
            daily_reward.user = user
            daily_reward.status = True
        daily_reward.save()
        if fetch_state == 1:
            sentCustomerMsg.apply_async(kwargs={
            "txt":"尊敬的用户，您的网利宝账号（%s）今天已经领取过红包花雨季奖励了,\n此微信号今日领取的奖励失效了~\n要记得，无法每天重复领取奖励哦，认真查看活动规则哦~~"%safe_phone_str(user.wanglibaouserprofile.phone),
            "openid":openid,
                },
                            queue='celery02')
        if fetch_state ==2:
            sentCustomerMsg.apply_async(kwargs={
            "txt":"恭喜您获得网利红包花雨季奖励\n成功领取：%s元现金红包\n快去我的账户 - 理财券页面查看吧！"%amount,
            "openid":openid,
                },
                            queue='celery02')
        return 0, "ok", amount

