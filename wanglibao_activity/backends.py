# encoding:utf-8

import time
import datetime
import json
import logging
import decimal
from django.utils import timezone
from django.db.models import Q
from models import Activity, ActivityRule, ActivityRecord
from marketing import helper
from marketing.models import IntroducedBy
from wanglibao_redpack import backends as redpack_backends

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
    print "====== trigger: %s, device: %s ======" % (trigger_node, device_type)
    #get all the activities
    activity_list = Activity.objects.filter(start_at__lt=now, end_at__gt=now, is_stopped=False, channel=channel)\
                                    .filter(Q(platform=device_type) | Q(platform=u'all'))
    if activity_list:
        for activity in activity_list:
            #get rules
            activity_rules = ActivityRule.objects.filter(activity=activity, trigger_node=trigger_node)
            if activity_rules:
                for rule in activity_rules:
                    if not rule.gift_type:
                        continue
                    else:
                        print "========= check start ========="
                        _check_rules_trigger(user, rule, trigger_node, device_type, amount)
            else:
                return
    else:
        return


def _check_rules_trigger(user, rule, trigger_node, device_type, amount):
    """ check the trigger node """
    if trigger_node == rule.trigger_node:
        #register or id validate
        if trigger_node in ('register', 'validation'):
            print "====== trigger_node: %s =======" % trigger_node
            _send_gift(user, rule, device_type)
        #pay, first pay, buy, first buy
        if trigger_node in ('pay', 'first_pay', 'buy', 'first_buy'):
            print "====== trigger_node: %s =======" % trigger_node
            if rule.min_amount == 0 and rule.max_amount == 0:
                _send_gift(user, rule, device_type)
            else:
                if rule.min_amount <= amount <= rule.max_amount:
                    _send_gift(user, rule, device_type)
        #p2p audit
        if rule.trigger_node == 'p2p_audit':
            #delay
            # _send_gift(user, rule, device_type)
            return
    else:
        return


def _send_gift(user, rule, device_type, amount=0):
    #send reward
    if rule.gift_type == 'reward':
        pass
    #send red pack
    if rule.gift_type == 'redpack':
        rtype = rule.trigger_node
        redpack_name = rule.redpack
        #send to
        print "======= do send, device: %s =========" % device_type
        if rule.send_type == 'sys_auto':
            redpack_backends.give_activity_redpack(user, rtype, redpack_name, device_type, rule_id)
        #insert record
        _save_activity_record(rule, user)
        #check do have the introduce relationship
        if rule.both_share:
            user_ib = _check_introduced_by(user)
            if user_ib:
                #to invite people red pack
                if rule.send_type == 'sys_auto':
                    redpack_backends.give_activity_redpack(user_ib, rtype, redpack_name, device_type, rule_id)
                _save_activity_record(rule, user_ib, True)
    #send income or amount
    if rule.gift_type == 'income':
        pass
    #送话费
    if rule.gift_type == 'phonefare':
        pass


def _check_introduced_by(user):
    ib = IntroducedBy.objects.filter(user=user).first()
    if ib:
        return ib.introduced_by
    return None

def _save_activity_record(rule, user, introduced_by=False):
    record = ActivityRecord()
    record.activity = rule.activity
    record.rule = rule
    record.platform = rule.activity.platform
    record.trigger_node = rule.trigger_node
    record.trigger_at = timezone.now()
    record.user = user
    record.income = rule.income
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