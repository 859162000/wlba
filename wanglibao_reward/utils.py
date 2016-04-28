# -*- coding: utf-8 -*-
import datetime
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
import json
from wanglibao_reward.models import WechatPhoneRewardRecord, P2pOrderRewardRecord
from wanglibao_activity.models import Activity, ActivityRule
from wanglibao_redpack.models import RedPack, RedPackEvent
from experience_gold.models import ExperienceEvent
from experience_gold.backends import SendExperienceGold
from wanglibao_redpack.backends import give_activity_redpack_for_hby, _send_message_for_hby, get_start_end_time
from marketing.utils import local_to_utc
from wanglibao_p2p.models import P2PRecord, P2PProduct
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_account.auth_backends import User
from wanglibao_redis.backend import redis_backend
from misc.models import Misc
import logging
import pickle
from decimal import Decimal
from weixin.util import getMiscValue
from wanglibao.templatetags.formatters import safe_phone_str
from marketing.models import Reward
from wanglibao_reward.models import WanglibaoRewardJoinRecord
from wanglibao_reward.models import WanglibaoActivityReward as ActivityReward
from wanglibao_account import message as inside_message
from wanglibao_sms.tasks import send_messages

logger = logging.getLogger('wanglibao_reward')

def sendWechatPhoneRewardByRegister(user, device_type="all"):
    phone = user.wanglibaouserprofile.phone
    phoneRewardRecords = WechatPhoneRewardRecord.objects.filter(status=False, phone=phone).all()
    for phoneRewardRecord in phoneRewardRecords:
        redpack_record_ids = ""
        experience_record_ids = ""
        rewards = getRewardsByActivity(phoneRewardRecord.activity_code)
        for key, value in rewards.iteritems():
            if key == 'redpack':
                for redpack_event_info in value:
                    redpack_event = redpack_event_info['redpack_event']
                    status, messege, record = give_activity_redpack_for_hby(user, redpack_event, device_type)
                    if status:
                        if not redpack_record_ids:
                            redpack_record_ids += str(record.id)
                        else:
                            redpack_record_ids += (","+str(record.id))
                        start_time, end_time = get_start_end_time(redpack_event.auto_extension, redpack_event.auto_extension_days,
                                                                  record.created_at, redpack_event.available_at, redpack_event.unavailable_at)
                        _send_message_for_hby(user, redpack_event, end_time)
            if key == 'experience':
                for experience_info in value:
                    experience = experience_info['experience_event']
                    experience_record_id, experience_event = SendExperienceGold(user).send(pk=experience.id)
                    if not experience_record_ids:
                        experience_record_ids += str(experience_record_id)
                    else:
                        experience_record_ids += (","+str(experience_record_id))
        redpack_ids = phoneRewardRecord.redpack_event_ids.split(',')
        for redpack_id in redpack_ids:
            redpack_event = RedPackEvent.objects.filter(id=int(redpack_id)).first()
            status, messege, record = give_activity_redpack_for_hby(user, redpack_event, device_type)
            if not redpack_record_ids:
                redpack_record_ids += str(record.id)
            else:
                redpack_record_ids += (","+str(record.id))
            if status:
                start_time, end_time = get_start_end_time(redpack_event.auto_extension, redpack_event.auto_extension_days,
                                                          record.created_at, redpack_event.available_at, redpack_event.unavailable_at)
                _send_message_for_hby(user, redpack_event, end_time)
        phoneRewardRecord.status = True
        phoneRewardRecord.redpack_record_ids = redpack_record_ids
        phoneRewardRecord.experience_record_ids = experience_record_ids
        phoneRewardRecord.save()

def sendWechatPhoneReward(openid, user, device_type):
    now_date = datetime.date.today()
    events = []
    records = []
    redpack_record_ids = ""
    experience_record_ids = ""
    with transaction.atomic():
        phoneRewardRecord = WechatPhoneRewardRecord.objects.select_for_update().filter(openid=openid, create_date=now_date).first()
        if not phoneRewardRecord.status:
            rewards = getRewardsByActivity(phoneRewardRecord.activity_code)
            for key, value in rewards.iteritems():
                if key == 'redpack':
                    for redpack_event_info in value:
                        redpack_event = redpack_event_info['redpack_event']
                        status, messege, record = give_activity_redpack_for_hby(user, redpack_event, device_type)
                        if not status:
                            return {"ret_code":-1, "message":messege}
                        if not redpack_record_ids:
                            redpack_record_ids += str(record.id)
                        else:
                            redpack_record_ids += (","+str(record.id))
                        events.append(redpack_event)
                        records.append(record)
                if key == 'experience':
                    for experience_info in value:
                        experience = experience_info['experience_event']
                        experience_record_id, experience_event = SendExperienceGold(user).send(pk=experience.id)
                        if not experience_record_id:
                            return {"ret_code":-1, "message":"体验金无法发放"}
                        if not experience_record_ids:
                            experience_record_ids += str(experience_record_id)
                        else:
                            experience_record_ids += (","+str(experience_record_id))

            redpack_ids = phoneRewardRecord.redpack_event_ids.split(',')
            for redpack_id in redpack_ids:
                redpack_event = RedPackEvent.objects.filter(id=int(redpack_id)).first()
                status, messege, record = give_activity_redpack_for_hby(user, redpack_event, device_type)
                if not status:
                    return {"ret_code":-1, "message":messege}
                if not redpack_record_ids:
                    redpack_record_ids += str(record.id)
                else:
                    redpack_record_ids += (","+str(record.id))
                events.append(redpack_event)
                records.append(record)
            phoneRewardRecord.status = True
            phoneRewardRecord.redpack_record_ids = redpack_record_ids
            phoneRewardRecord.experience_record_ids = experience_record_ids
            phoneRewardRecord.save()
    try:
        for idx, event in enumerate(events):
            record = records[idx]
            start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                                      record.created_at, event.available_at, event.unavailable_at)
            _send_message_for_hby(user, event, end_time)
    except Exception, e:
        pass
    return {"ret_code":0, "message": "发放完成"}




def getRewardsByActivity(code):
    rewards = {'redpack':[], 'experience':[]}
    activity = Activity.objects.filter(code=code).first()
    activity_rules = ActivityRule.objects.filter(activity=activity, is_used=True).all()
    for activity_rule in activity_rules:
        if activity_rule.gift_type == "redpack":
            redpack_ids = activity_rule.redpack.split(',')
            for redpack_id in redpack_ids:
                redpack_event = RedPackEvent.objects.filter(id=redpack_id).first()
                if redpack_event.rtype == "interest_coupon":
                    rewards.get('redpack').append({"redpack_event":redpack_event, "priority":1})
                else:
                    rewards.get('redpack').append({"redpack_event":redpack_event, "priority":0})
        if activity_rule.gift_type == "experience_gold":
            now = timezone.now()
            experience = ExperienceEvent.objects.filter(invalid=False, pk=activity_rule.redpack, available_at__lt=now, unavailable_at__gt=now).first()
            if experience:
                rewards.get('experience').append({'experience_event':experience})
    return rewards

def getTodayTop10Ranks():
    today = datetime.datetime.now()
    today_start = local_to_utc(today, 'min')
    today_end = local_to_utc(today, 'max')
    top_ranks = P2PRecord.objects.filter(catalog='申购', create_time__gte=today_start, create_time__lte=today_end).values('user').annotate(Sum('amount')).order_by('-amount__sum')[:10]
    uids = [rank['user'] for rank in top_ranks]
    userprofiles = WanglibaoUserProfile.objects.filter(user__in=uids).all()
    for rank in top_ranks:
        for userprofile in userprofiles:
            if userprofile.user_id == rank['user']:
                rank['phone'] = safe_phone_str(userprofile.phone)
                
                break
    return top_ranks


def getYesterdayTop10Ranks():
    yesterday = datetime.datetime.now()-datetime.timedelta(1)
    yesterday_start = local_to_utc(yesterday, 'min')
    yesterday_end = local_to_utc(yesterday, 'max')
    top_ranks = P2PRecord.objects.filter(catalog='申购', create_time__gte=yesterday_start, create_time__lte=yesterday_end).values('user').annotate(Sum('amount')).order_by('-amount__sum')[:10]
    return top_ranks


def updateRedisTopRank():
    top_ranks = []
    try:
        top_ranks = getTodayTop10Ranks()
        redis = redis_backend()
        redis._set('top_ranks', pickle.dumps(top_ranks))
    except Exception,e:
        logger.error("====updateRedisTopRank======="+e.message)
    return top_ranks


def getWeekTop10Ranks():
    #today = datetime.datetime.now()
    #计算开始时间从上周六0点开始
    #week_frist_day = today + datetime.timedelta(days=-int(today.strftime('%u'))+1-2)
    week_frist_day = getWeekBeginDay()
    today_start = local_to_utc(week_frist_day, 'min')
    #today_end = local_to_utc(today, 'max')
    top_ranks = P2PRecord.objects.filter(catalog='申购', create_time__gte=today_start).values('user').annotate(Sum('amount')).order_by('-amount__sum')[:10]
    uids = [rank['user'] for rank in top_ranks]
    userprofiles = WanglibaoUserProfile.objects.filter(user__in=uids).all()
    for rank in top_ranks:
        for userprofile in userprofiles:
            if userprofile.user_id == rank['user']:
                rank['phone'] = safe_phone_str(userprofile.phone)
                break
    return top_ranks

def updateRedisWeekTopRank():
    top_ranks = []
    try:
        top_ranks = getWeekTop10Ranks()
        redis = redis_backend()
        today = datetime.datetime.now()
        week_top_ranks = 'week_top_ranks_' + today.strftime('%Y_%m_%d')
        redis._set(week_top_ranks, pickle.dumps(top_ranks))
    except Exception,e:
        logger.error("====updateRedisWeekTopRank======="+e.message)
    return top_ranks

def getWeekSum():
    amount_week_sum = 0
    try:
        #today = datetime.datetime.now()
        #week_frist_day = today + datetime.timedelta(days=-int(today.strftime('%u'))+1-2)
        week_frist_day = getWeekBeginDay()
        today_start = local_to_utc(week_frist_day, 'min')
        #today_end = local_to_utc(today, 'max')
        #week_sum = P2PRecord.objects.filter(catalog='申购', create_time__gte=today_start, create_time__lte=today_end).aggregate(Sum('amount'))
        week_sum = P2PRecord.objects.filter(catalog='申购', create_time__gte=today_start).aggregate(Sum('amount'))
        amount_week_sum = week_sum['amount__sum'] if week_sum['amount__sum'] else Decimal('0')
    except Exception,e:
        logger.error("====updateRedisWeekTopRank======="+e.message)
    return amount_week_sum 

def getWeekBeginDay():
    today = datetime.datetime.now()
    delta_days = int(today.strftime('%u')) - 6
    if delta_days<0:
        delta_days = delta_days + 7
    week_frist_day = today - datetime.timedelta(days=delta_days)
    return week_frist_day

def updateRedisWeekSum():
    top_ranks = 0
    try:
        top_ranks = getWeekSum()
        redis = redis_backend()
        today = datetime.datetime.now()
        week_sum = 'week_sum_' + today.strftime('%Y_%m_%d')
        redis._set(week_sum, pickle.dumps(top_ranks))
    except Exception,e:
        logger.error("====updateRedisWeekSum======="+e.message)
    return top_ranks

def processMarchAwardAfterP2pBuy(user, product_id, order_id, amount):
    try:
        status = int(getMiscValue('april_reward').get('status',0))
        if status==1:
            updateRedisWeekSum()
            updateRedisWeekTopRank()
    except Exception, e:
        logger.error("===========processMarchAwardAfterP2pBuy==================="+e.message)


def processMarchAwardAfterP2pBuy_March(user, product_id, order_id, amount):
    try:
        product = P2PProduct.objects.filter(id=product_id).get()
        if product:
            rank_activity = Activity.objects.filter(code='march_awards').first()
            utc_now = timezone.now()
            if rank_activity and not rank_activity.is_stopped and rank_activity.start_at<=utc_now and rank_activity.end_at>=utc_now:
                # updateRedisTopRank.apply_async()
                updateRedisTopRank()

                period = product.period
                if product.pay_method.startswith(u'日计息'):
                    period = product.period/30
                if period >= 3:
                    misc = Misc.objects.filter(key='march_awards').first()
                    march_awards = json.loads(misc.value)
                    if march_awards and isinstance(march_awards, dict):
                        highest = march_awards.get('highest', 0)
                        lowest = march_awards.get('lowest', 0)

                        if float(amount) >= float(lowest) and float(amount) < float(highest):
                            P2pOrderRewardRecord.objects.create(
                                user=user,
                                activity_desc=u'投资额度奖励',
                                order_id=order_id,
                                )
    except Exception, e:
        logger.error("===========processMarchAwardAfterP2pBuy==================="+e.message)


def processAugustAwardZhaoXiangGuan(user, product_id, order_id, amount):
    key = 'zhaoxiangguan'
    activity_config = Misc.objects.filter(key=key).first()
    if activity_config:
        activity = json.loads(activity_config.value)
        if type(activity) == dict:
            try:
                start_time = activity['start_time']
                end_time = activity['end_time']
            except KeyError, reason:
                logger.debug(u"misc中activities配置错误，请检查,reason:%s" % reason)
                raise Exception(u"misc中activities配置错误，请检查，reason:%s" % reason)
        else:
            raise Exception(u"misc中activities的配置参数，应是字典类型")
    else:
        raise Exception(u"misc中没有配置activities杂项")

    p2p_record = P2PRecord.objects.filter(user_id=user.id, catalog=u'申购').order_by('create_time').first()
    if not p2p_record:
        raise Exception(u"购买订单异常")

    #TODO:转换为UTC时间后跟表记录时间对比
    from wanglibao_account import utils
    utc_start = (utils.ext_str_to_utc(start_time)).strftime("%Y-%m-%d %H:%M:%S")
    utc_end = (utils.ext_str_to_utc(end_time)).strftime("%Y-%m-%d %H:%M:%S")
    now = p2p_record.create_time.strftime("%Y-%m-%d %H:%M:%S")
    if now < utc_start or now >= utc_end:
        #raise Exception(u"活动还未开始,请耐心等待")
            return

    #判断有没有奖品剩余
    with transaction.atomic:
        reward = Reward.objects.select_for_update().filter(type='影像投资节优惠码', is_used=False).first()
        if reward == None:
            raise Exception(u"奖品已经发完了")
        else:
            reward.is_used = True
            reward.save()
            
    try:
        with transaction.atomic():
            join_record = WanglibaoRewardJoinRecord.objects.select_for_update().filter(user=user, activity_code='sy').first()
            if not join_record:
                join_record = WanglibaoRewardJoinRecord.objects.create(
                    user=user,
                    activity_code='sy',
                    remain_chance=0,
                )

            reward_record = ActivityReward.objects.filter(has_sent=True, activity='sy', user=user).first()
            if reward_record:  #奖品记录已经生成了
                reward.is_used = False
                reward.save()
                return

            ActivityReward.objects.create(
                        activity='sy',
                        order_id=order_id,
                        user=user,
                        p2p_amount=p2p_record.amount,
                        reward=reward,
                        has_sent=True,
                        left_times=0,
                        join_times=0)
    except Exception:
        reward.is_used = False
        reward.save()
        raise Exception(u"发奖异常，奖品回库")
    else:
        send_msg = u'尊敬的用户，恭喜您在参与影像投资节活动中获得优惠机会，优惠码为：%s，'\
                   u'请凭借此信息至相关门店享受优惠，相关奖励请咨询八月婚纱照相馆及鼎极写真摄影，'\
                   u'感谢您的参与！【网利科技】' % (send_reward.content)
        send_messages.apply_async(kwargs={
            "phones": [user.id, ],
            "message": [send_msg, ],
        })
        inside_message.send_one.apply_async(kwargs={
            "user_id": user.id,
            "title": u"影像投资节优惠码",
            "content": send_msg,
            "mtype": "activity"
        })