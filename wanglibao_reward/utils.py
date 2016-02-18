# -*- coding: utf-8 -*-
import datetime
from django.utils import timezone
from django.db import transaction
from wanglibao_reward.models import WechatPhoneRewardRecord
from wanglibao_activity.models import Activity, ActivityRule
from wanglibao_redpack.models import RedPack, RedPackEvent
from experience_gold.models import ExperienceEvent
from experience_gold.backends import SendExperienceGold
from wanglibao_redpack.backends import give_activity_redpack_for_hby, _send_message_for_hby, get_start_end_time

def sendWechatPhoneRewardByRegister(user, device_type="all"):
    phone = user.wanglibaouserprofile.phone
    phoneRewardRecords = WechatPhoneRewardRecord.objects.filter(status=False, phone=phone).all()
    for phoneRewardRecord in phoneRewardRecords:
        rewards = getRewardsByActivity(phoneRewardRecord.activity_code)
        for key, value in rewards.iteritems():
            if key == 'redpack':
                for redpack_event_info in value:
                    redpack_event = redpack_event_info['redpack_event']
                    status, messege, record = give_activity_redpack_for_hby(user, redpack_event, device_type)
                    if status:

                        start_time, end_time = get_start_end_time(redpack_event.auto_extension, redpack_event.auto_extension_days,
                                                                  record.created_at, redpack_event.available_at, redpack_event.unavailable_at)
                        _send_message_for_hby(user, redpack_event, end_time)
            if key == 'experience':
                for experience_info in value:
                    experience = experience_info['experience']
                    SendExperienceGold(user).send(pk=experience.id)

        redpack_ids = phoneRewardRecord.redpack_event_ids.split(',')
        for redpack_id in redpack_ids:
            redpack_event = RedPackEvent.objects.filter(id=int(redpack_id)).first()
            status, messege, record = give_activity_redpack_for_hby(user, redpack_event, device_type)
            if status:
                start_time, end_time = get_start_end_time(redpack_event.auto_extension, redpack_event.auto_extension_days,
                                                          record.created_at, redpack_event.available_at, redpack_event.unavailable_at)
                _send_message_for_hby(user, redpack_event, end_time)
        phoneRewardRecord.status = True
        phoneRewardRecord.save()

def sendWechatPhoneReward(openid, user, device_type):
    now_date = datetime.date.today()
    events = []
    records = []
    with transaction.atomic():
        phoneRewardRecord = WechatPhoneRewardRecord.objects.select_for_update().filter(status=False, openid=openid, create_date=now_date).first()
        rewards = getRewardsByActivity(phoneRewardRecord.activity_code)
        for key, value in rewards.iteritems():
            if key == 'redpack':
                for redpack_event_info in value:
                    redpack_event = redpack_event_info['redpack_event']
                    status, messege, record = give_activity_redpack_for_hby(user, redpack_event, device_type)
                    if not status:
                        return {"ret_code":-1, "message":messege}
                    events.append(redpack_event)
                    records.append(record)
            if key == 'experience':
                for experience_info in value:
                    experience = experience_info['experience']
                    experience_record_id, experience_event = SendExperienceGold(user).send(pk=experience.id)
                    if not experience_record_id:
                        return {"ret_code":-1, "message":"体验金无法发放"}

        redpack_ids = phoneRewardRecord.redpack_event_ids.split(',')
        for redpack_id in redpack_ids:
            redpack_event = RedPackEvent.objects.filter(id=int(redpack_id)).first()
            status, messege, record = give_activity_redpack_for_hby(user, redpack_event, device_type)
            if not status:
                return {"ret_code":-1, "message":messege}
            events.append(redpack_event)
            records.append(record)
        phoneRewardRecord.status = True
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

