# encoding:utf-8

import time
import datetime
import json
import logging
import decimal
from django.utils import timezone
from django.db.models import Q
from django.db import transaction
from django.template import Template, Context
from models import Activity, ActivityRule, ActivityRecord
from marketing import helper
from marketing.models import IntroducedBy, Reward, RewardRecord
from wanglibao_redpack import backends as redpack_backends
from wanglibao_pay.models import PayInfo
from wanglibao_p2p.models import P2PRecord
from wanglibao_account import message as inside_message
from wanglibao.templatetags.formatters import safe_phone_str
from wanglibao_sms.tasks import send_messages

logger = logging.getLogger(__name__)


def _decide_device(device_type):
    device_type = device_type.lower()
    if device_type == 'pc':
        return 'pc'
    elif device_type == 'ios':
        return 'ios'
    elif device_type == 'android':
        return 'android'
    else:
        return 'all'


def check_activity(user, trigger_node, device_type, amount=0):
    now = timezone.now()
    device_type = _decide_device(device_type)
    if not trigger_node:
        return
    # ib = IntroducedBy.objects.filter(user=user).first()
    # if not ib or not ib.channel:
    #     channel = 'wanglibao'
    # else:
    #     channel = ib.channel.name
    channel = helper.which_channel(user)
    print "====== trigger: %s, device: %s ====== \n" % (trigger_node, device_type)
    print "====== now: %s =======" % now
    #查询符合条件的活动
    activity_list = Activity.objects.filter(start_at__lt=now, end_at__gt=now, is_stopped=False, channel=channel)\
                                    .filter(Q(platform=device_type) | Q(platform=u'all'))
    if activity_list:
        for activity in activity_list:
            #查询活动规则
            activity_rules = ActivityRule.objects.filter(activity=activity, trigger_node=trigger_node, is_used=True)
            if activity_rules:
                for rule in activity_rules:
                    if not rule.gift_type:
                        continue
                    else:
                        print "========= check start ========="
                        if rule.is_introduced:
                            user_ib = _check_introduced_by(user)
                            if user_ib:
                                _check_rules_trigger(user, rule, trigger_node, device_type, amount)
                        else:
                            _check_rules_trigger(user, rule, trigger_node, device_type, amount)
            else:
                return
    else:
        return


def _check_rules_trigger(user, rule, trigger_node, device_type, amount):
    """ check the trigger node """
    if trigger_node == rule.trigger_node:
        #注册 或 实名认证
        if trigger_node in ('register', 'validation'):
            print "====== trigger_node: %s =======" % trigger_node
            _send_gift(user, rule, device_type)
        #充值 (pay, first_pay)
        if trigger_node == 'recharge':
            print "====== recharge trigger_node: %s =======" % trigger_node
            is_amount = _check_amount(rule.min_amount, rule.max_amount, amount)
            if is_amount:
                if rule.trigger_node == 'first_pay':
                    #check first pay
                    if PayInfo.objects.filter(user=user, type='D',
                                              update_time__gt=rule.activity.start_at,
                                              status=PayInfo.SUCCESS).count() == 1:
                        _send_gift(user, rule, device_type, amount)
                if rule.trigger_node == 'pay':
                    _send_gift(user, rule, device_type, amount)
        #投资 (buy, first_buy)
        if trigger_node == 'invest':
            print "====== invest trigger_node: %s =======" % trigger_node
            is_amount = _check_amount(rule.min_amount, rule.max_amount, amount)
            if is_amount:
                if rule.trigger_node == 'first_buy':
                    #check first pay
                    if P2PRecord.objects.filter(user=user,
                                                create_time__gt=rule.activity.start_at).count() == 1:
                        _send_gift(user, rule, device_type, amount)
                if rule.trigger_node == 'buy':
                    _send_gift(user, rule, device_type, amount)
        #p2p audit
        if rule.trigger_node == 'p2p_audit':
            #delay
            # _send_gift(user, rule, device_type)
            return
    else:
        return


def _send_gift(user, rule, device_type, amount=0):
    # rule_id = rule.id
    rtype = rule.trigger_node
    is_amount = _check_amount(rule.min_amount, rule.max_amount, amount)
    #送奖品
    if rule.gift_type == 'reward':
        reward_name = rule.reward
        print "======do send reward, device : %s =======" % device_type
        if amount and amount > 0:
            if is_amount:
                _send_gift_reward(user, rule, rtype, reward_name, device_type)
        else:
            _send_gift_reward(user, rule, rtype, reward_name, device_type)

    #送红包
    if rule.gift_type == 'redpack':
        redpack_name = rule.redpack
        #此处后期要加上检测红包数量的逻辑，数量不够就记录下没有发送的用户，并通知市场相关人员
        #send to
        print "======= do send redpack, device: %s =========" % device_type
        if amount and amount > 0:
            if is_amount:
                _send_gift_redpack(user, rule, rtype, redpack_name, device_type)
        else:
            _send_gift_redpack(user, rule, rtype, redpack_name, device_type)
    #送现金或收益
    if rule.gift_type == 'income':
        #send to
        print "======= do send income, device: %s =========" % device_type
        if amount and amount > 0:
            if is_amount:
                _send_gift_income(user, rule)
        else:
            _send_gift_income(user, rule)

    #送话费
    if rule.gift_type == 'phonefare':
        #send to
        print "======= do send phonefare, device: %s =========" % device_type
        if amount and amount > 0:
            if is_amount:
                _send_gift_phonefare(user, rule)
        else:
            _send_gift_phonefare(user, rule)


def _check_introduced_by(user):
    ib = IntroducedBy.objects.filter(user=user).first()
    if ib:
        return ib.introduced_by
    return None


def _check_amount(min_amount, max_amount, amount):
    if amount == 0:
        return False
    else:
        if min_amount == 0 and max_amount ==0:
            return True
        elif min_amount > 0 and max_amount == 0:
            if amount >= min_amount:
                return True
            else:
                return False
        else:
            if min_amount < amount <= max_amount:
                return True
            else:
                return False


def _send_gift_reward(user, rule, rtype, reward_name, device_type):
    now = timezone.now()
    if rule.send_type == 'sys_auto':
        #do send
        _send_reward(user, rule, rtype, reward_name)
        if rule.both_share:
            user_introduced_by = _check_introduced_by(user)
            if user_introduced_by:
                _send_reward(user_introduced_by, rule, rtype, reward_name)
    else:
        #只记录不发信息
        _save_activity_record(rule, user, 'only_record')
        if rule.both_share:
            _save_activity_record(rule, user, 'only_record', True)


def _send_reward(user, rule, rtype, reward_name):
    now = timezone.now()
    reward = Reward.objects.filter(type=reward_name,
                                   is_used=False,
                                   end_time__gte=now).first()
    if reward:
        reward.is_used = True
        reward.save()
        description = '>'.join([rtype, reward_name])
        #记录奖品发放流水
        has_reward_record = _keep_reward_record(user, reward, description)
        if has_reward_record:
            #发放站内信或短信
            _send_message_sms(user, rule, reward)


def _send_gift_income(user, rule):
    # now = timezone.now()
    income = rule.income
    if income > 0:
        if rule.send_type == 'sys_auto':
            _send_message_sms(user, rule)
            if rule.both_share:
                user_introduced_by = _check_introduced_by(user)
                if user_introduced_by:
                    _send_message_sms(user_introduced_by, rule)
        else:
            #只记录不发信息
            _save_activity_record(rule, user, 'only_record')
            if rule.both_share:
                _save_activity_record(rule, user, 'only_record', True)
    else:
        return


def _send_gift_phonefare(user, rule):
    # now = timezone.now()
    phone_fare = rule.income
    if phone_fare > 0:
        if rule.send_type == 'sys_auto':
            _send_message_sms(user, rule)
            if rule.both_share:
                user_introduced_by = _check_introduced_by(user)
                if user_introduced_by:
                    _send_message_sms(user_introduced_by, rule)
        else:
            #只记录不发信息
            _save_activity_record(rule, user, 'only_record')
            if rule.both_share:
                _save_activity_record(rule, user, 'only_record', True)
    else:
        return


def _send_gift_redpack(user, rule, rtype, redpack_name, device_type):
    if rule.send_type == 'sys_auto':
        redpack_backends.give_activity_redpack_new(user, rtype, redpack_name, device_type, rule.id)
    #insert record
    _save_activity_record(rule, user, 'message')
    #check do have the introduce relationship
    if rule.both_share:
        user_ib = _check_introduced_by(user)
        if user_ib:
            #to invite people red pack
            if rule.send_type == 'sys_auto':
                redpack_backends.give_activity_redpack_new(user_ib, rtype, redpack_name, device_type, rule.id)
            _save_activity_record(rule, user_ib, 'message', True)


def _save_activity_record(rule, user, msg_type, introduced_by=False):
    record = ActivityRecord()
    record.activity = rule.activity
    record.rule = rule
    record.platform = rule.activity.platform
    record.trigger_node = rule.trigger_node
    record.trigger_at = timezone.now()
    record.user = user
    record.income = rule.income
    record.msg_type = msg_type
    if msg_type == 'only_record':
        description = u''
    else:
        if rule.send_type == 'sys_auto':
            description = u'【系统发放】'
        else:
            description = u'【需人工发放】'
    if introduced_by:
        share_txt = u'【邀请人获得】'
        description = ''.join([description, share_txt])
    if rule.gift_type == 'redpack':
        description = ''.join([description, rule.redpack])
    if rule.gift_type == 'reward':
        description = ''.join([description + rule.reward])
    record.description = description
    record.save()


def _send_message_sms(user, rule, reward):
    title = rule.rule_name
    msg_template = rule.msg_template
    sms_template = rule.sms_template
    mobile = user.wanglibaouserprofile.phone
    inviter_phone, invited_phone = '', ''
    introduced_by = IntroducedBy.objects.filter(user=user).first()
    if introduced_by and introduced_by.introduced_by:
        inviter_phone = introduced_by.introduced_by.wanglibaouserprofile.phone
        invited_phone = introduced_by.user.wanglibaouserprofile.phone
        inviter_phone = safe_phone_str(inviter_phone)
        invited_phone = safe_phone_str(invited_phone)
    context = Context({
        'mobile': safe_phone_str(mobile),
        'reward': reward.content,
        'inviter': inviter_phone,
        'invited': invited_phone,
        'amount': rule.income
    })
    if msg_template:
        msg = Template(msg_template)
        content = msg.render(context)
        _send_message_template(user, title, content)
        _save_activity_record(rule, user, 'message')
    if sms_template:
        sms = Template(sms_template)
        content = sms.render(context) + u'回复TD退订 4008-588-066【网利宝】'
        _send_sms_template(safe_phone_str(mobile), content)
        _save_activity_record(rule, user, 'sms')


def _keep_reward_record(user, reward, description=''):
    try:
        RewardRecord.objects.create(user=user,
                                    reward=reward,
                                    description=description)
        return True
    except Exception, e:
        return False


def _send_message_template(user, title, content):
    inside_message.send_one.apply_async(kwargs={
        "user_id": user.id,
        "title": title,
        "content": content,
        "mtype": "activity"
    })


def _send_sms_template(phones, content):
    send_messages.apply_async(kwargs={
        "phones": [phones, ],
        "messages": [content, ]
    })

