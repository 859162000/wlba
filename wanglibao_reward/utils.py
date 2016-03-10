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
                rank['phone'] = userprofile.phone
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
        redis_backend()._lpush('top_ranks', top_ranks)
    except Exception,e:
        logger.error("====updateRedisTopRank======="+e.message)
    return top_ranks

def processMarchAwardAfterP2pBuy(user, product_id, order_id, amount):
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

                        if float(amount) >= lowest and float(amount) <= highest:
                            P2pOrderRewardRecord.objects.create(
                                user=user,
                                activity_desc=u'投资额度奖励',
                                order_id=order_id,
                                )
    except Exception, e:
        logger.error("===========processMarchAwardAfterP2pBuy==================="+e.message)
