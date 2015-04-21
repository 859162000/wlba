# encoding:utf-8

import time
import datetime
import json
import logging
import decimal
from django.utils import timezone
from django.db.models import Q, Sum
from django.db import transaction
from django.template import Template, Context
from models import Activity, ActivityRule, ActivityRecord
from marketing import helper
from marketing.models import IntroducedBy, Reward, RewardRecord
from wanglibao_redpack import backends as redpack_backends
from wanglibao_redpack.models import RedPackEvent
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


def check_activity(user, trigger_node, device_type, amount=0, product_id=0, is_full=False):
    now = timezone.now()
    device_type = _decide_device(device_type)
    if not trigger_node:
        return
    channel = helper.which_channel(user)
    #查询符合条件的活动
    activity_list = Activity.objects.filter(start_at__lt=now, end_at__gt=now, is_stopped=False, channel__contains=channel)\
                                    .filter(Q(platform=device_type) | Q(platform=u'all')).order_by('-id')
    if activity_list:
        for activity in activity_list:
            #查询活动规则
            if trigger_node == 'invest':
                activity_rules = ActivityRule.objects.filter(activity=activity,  is_used=True)\
                    .filter(Q(trigger_node='buy') | Q(trigger_node='first_buy')).order_by('-id')
            elif trigger_node == 'recharge':
                activity_rules = ActivityRule.objects.filter(activity=activity,  is_used=True) \
                    .filter(Q(trigger_node='pay') | Q(trigger_node='first_pay')).order_by('-id')
            else:
                activity_rules = ActivityRule.objects.filter(activity=activity, trigger_node=trigger_node,
                                                             is_used=True).order_by('-id')

            if activity_rules:
                for rule in activity_rules:
                    if rule.is_introduced:
                        user_ib = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
                        if user_ib:
                            _check_rules_trigger(user, rule, rule.trigger_node, device_type, amount, product_id, is_full)
                    else:
                        _check_rules_trigger(user, rule, rule.trigger_node, device_type, amount, product_id, is_full)
            else:
                continue
    else:
        return


def _check_rules_trigger(user, rule, trigger_node, device_type, amount, product_id, is_full):
    """ check the trigger node """
    product_id = int(product_id)
    #注册 或 实名认证
    if trigger_node in ('register', 'validation'):
        _send_gift(user, rule, device_type)
    #首次充值
    elif trigger_node == 'first_pay':
        #check first pay
        if rule.is_in_date:
            first_pay_num = PayInfo.objects.filter(user=user, type='D',
                                                   update_time__gt=rule.activity.start_at,
                                                   status=PayInfo.SUCCESS).count()
        else:
            first_pay_num = PayInfo.objects.filter(user=user, type='D',
                                                   status=PayInfo.SUCCESS).count()
        if first_pay_num == 1:
            _check_trade_amount(user, rule, device_type, amount)
    #充值
    elif trigger_node == 'pay':
        _check_trade_amount(user, rule, device_type, amount)
    #首次购买
    elif trigger_node == 'first_buy':
        #check first pay
        if rule.is_in_date:
            first_buy_num = P2PRecord.objects.filter(user=user,
                                                     create_time__gt=rule.activity.start_at).count()
        else:
            first_buy_num = P2PRecord.objects.filter(user=user).count()

        if first_buy_num == 1:
            #判断当前购买产品id是否在活动设置的id中
            if product_id > 0 and rule.activity.product_ids:
                is_product = _check_product_id(product_id, rule.activity.product_ids)
                if is_product:
                    _check_buy_product(user, rule, device_type, amount, product_id, is_full)
            else:
                _check_buy_product(user, rule, device_type, amount, product_id, is_full)

    #购买
    elif trigger_node == 'buy':
        if product_id > 0 and rule.activity.product_ids:
            is_product = _check_product_id(product_id, rule.activity.product_ids)
            if is_product:
                _check_buy_product(user, rule, device_type, amount, product_id, is_full)
        else:
            _check_buy_product(user, rule, device_type, amount, product_id, is_full)
    #满标审核
    elif trigger_node == 'p2p_audit':
        #delay
        # _send_gift(user, rule, device_type)
        return
    else:
        return


def _send_gift(user, rule, device_type, amount=0):
    # rule_id = rule.id
    rtype = rule.trigger_node
    #送奖品
    if rule.gift_type == 'reward':
        reward_name = rule.reward
        _send_gift_reward(user, rule, rtype, reward_name, device_type, amount)

    #送红包
    if rule.gift_type == 'redpack':
        redpack_id = int(rule.redpack)
        #此处后期要加上检测红包数量的逻辑，数量不够就记录下没有发送的用户，并通知市场相关人员
        _send_gift_redpack(user, rule, rtype, redpack_id, device_type)

    #送现金或收益
    if rule.gift_type == 'income':
        #send to
        _send_gift_income(user, rule, amount)

    #送话费
    if rule.gift_type == 'phonefare':
        #send to
        _send_gift_phonefare(user, rule, amount)


def _check_introduced_by(user, start_dt, is_invite_in_date):
    if is_invite_in_date:
        ib = IntroducedBy.objects.filter(user=user, created_at__gt=start_dt).first()
    else:
        ib = IntroducedBy.objects.filter(user=user).first()

    if ib:
        return ib.introduced_by
    else:
        return None


def _check_buy_product(user, rule, device_type, amount, product_id, is_full):
    #检查单标投资顺序是否设置数字
    ranking_num = int(rule.ranking)
    if ranking_num > 0:
        #查询单标投资顺序
        records = P2PRecord.objects.filter(product__id=product_id, catalog=u'申购') \
                                   .order_by('create_time')
        if records:
            this_record = records[ranking_num-1]
            if this_record.user.id == user.id:
                _send_gift(user, rule, device_type)
    elif ranking_num == -1 and is_full is True:
        #查询是否满标，满标时不再考虑最小/最大金额，直接发送
        _send_gift(user, rule, device_type)
    else:
        _check_trade_amount(user, rule, device_type, amount)

    #判断单标累计投资名次
    if rule.is_total_invest and is_full is True:
        total_invest_order = int(rule.total_invest_order)
        if total_invest_order > 0:
            #按用户查询单标投资的总金额
            records = P2PRecord.objects.filter(product__id=product_id, catalog=u'申购').values('user') \
                                       .annotate(amount_sum=Sum('amount')) \
                                       .extra({'amount_sum': Sum('amount')}).order_by('-amount_sum')
            if records:
                record = records[total_invest_order-1]
                if record['user'] == user.id:
                    #如果设置了最小金额，则判断用户的投资总额是否在最大最小金额区间
                    amount_sum = record['amount_sum']
                    is_amount = _check_amount(rule.min_amount, rule.max_amount, amount_sum)
                    if is_amount:
                        _send_gift(user, rule, device_type)
        # else:
        #     #直接取当前用户的投资总额
        #     record = P2PRecord.objects.filter(product__id=product_id, user=user, catalog=u'申购')\
        #                               .extra({'amount_sum': Sum('amount')}).first()
        #     if record:
        #         amount_sum = record.amount_sum
        #         is_amount = _check_amount(rule.min_amount, rule.max_amount, amount_sum)
        #         if is_amount:
        #             _send_gift(user, rule, device_type)


def _check_trade_amount(user, rule, device_type, amount):
    is_amount = _check_amount(rule.min_amount, rule.max_amount, amount)
    if amount and amount > 0:
        if is_amount:
            _send_gift(user, rule, device_type, amount)
    else:
        _send_gift(user, rule, device_type, amount)


def _check_amount(min_amount, max_amount, amount):
    min_amount = int(min_amount)
    max_amount = int(max_amount)
    amount = int(amount)
    if amount == 0:
        return False
    else:
        if min_amount == 0 and max_amount == 0:
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


def _check_product_id(product_id, product_ids):
    if product_ids:
        product_ids_arr = product_ids.split(',')
        product_ids_arr = [int(pid) for pid in product_ids_arr if pid != '']
        if product_id in product_ids_arr:
            return True
        else:
            return False
    else:
        return False


def _send_gift_reward(user, rule, rtype, reward_name, device_type, amount):
    now = timezone.now()
    if rule.send_type == 'sys_auto':
        #do send
        _send_reward(user, rule, rtype, reward_name, None, amount)
        if rule.both_share:
            user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
            if user_introduced_by:
                _send_reward(user, rule, rtype, reward_name, user_introduced_by, amount)
    else:
        #只记录不发信息
        _save_activity_record(rule, user, 'only_record', reward_name)
        if rule.both_share:
            user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
            if user_introduced_by:
                _save_activity_record(rule, user_introduced_by, 'only_record', reward_name, True)


def _send_reward(user, rule, rtype, reward_name, user_introduced_by=None, amount=0):
    now = timezone.now()
    reward = Reward.objects.filter(type=reward_name,
                                   is_used=False,
                                   end_time__gte=now).first()
    if reward:
        reward.is_used = True
        reward.save()
        description = '=>'.join([rtype, reward.type])
        #记录奖品发放流水
        has_reward_record = _keep_reward_record(user, reward, description)
        if has_reward_record:
            #发放站内信或短信
            if user_introduced_by:
                _send_message_sms(user, rule, user_introduced_by, reward, amount)
            else:
                _send_message_sms(user, rule, None, reward, amount)


def _send_gift_income(user, rule, amount):
    # now = timezone.now()
    income = rule.income
    if income > 0:
        if rule.send_type == 'sys_auto':
            _send_message_sms(user, rule, None, None, amount)
            if rule.both_share:
                user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
                if user_introduced_by:
                    _send_message_sms(user, rule, user_introduced_by, None, amount)
        else:
            #只记录不发信息
            _save_activity_record(rule, user, 'only_record', rule.rule_name)
            if rule.both_share:
                user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
                if user_introduced_by:
                    _save_activity_record(rule, user_introduced_by, 'only_record', rule.rule_name, True)
    else:
        return


def _send_gift_phonefare(user, rule, amount):
    # now = timezone.now()
    phone_fare = rule.income
    if phone_fare > 0:
        if rule.send_type == 'sys_auto':
            _send_message_sms(user, rule, None, None, amount)
            if rule.both_share:
                user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
                if user_introduced_by:
                    _send_message_sms(user, rule, user_introduced_by, None, amount)
        else:
            #只记录不发信息
            _save_activity_record(rule, user, 'only_record', rule.rule_name)
            if rule.both_share:
                user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
                if user_introduced_by:
                    _save_activity_record(rule, user_introduced_by, 'only_record', rule.rule_name, True)
    else:
        return


def _send_gift_redpack(user, rule, rtype, redpack_id, device_type):
    """ 红包模板目前仍沿用红包模块的模板，以后需要时再更改；
        另外红包会发送短信和站内信，因此，此处记录流水时两者都记录。
    """
    if rule.send_type == 'sys_auto':
        redpack_backends.give_activity_redpack_new(user, rtype, redpack_id, device_type, rule.id)
    #记录流水，目前红包系同时发送站内信和短信，因此此处记录两条流水，下同
    _save_activity_record(rule, user, 'message', rule.rule_name)
    _save_activity_record(rule, user, 'sms', rule.rule_name)
    #检测是否有邀请关系
    if rule.both_share:
        user_ib = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
        if user_ib:
            #给邀请人发红包
            if rule.send_type == 'sys_auto':
                redpack_backends.give_activity_redpack_new(user_ib, rtype, redpack_id, device_type, rule.id)
            _save_activity_record(rule, user_ib, 'message', rule.rule_name, True)
            _save_activity_record(rule, user_ib, 'sms', rule.rule_name, True)


def _save_activity_record(rule, user, msg_type, msg_content='', introduced_by=False):
    record = ActivityRecord()
    record.activity = rule.activity
    record.rule = rule
    record.platform = rule.activity.platform
    record.trigger_node = rule.trigger_node
    record.trigger_at = timezone.now()
    record.user = user
    record.income = rule.income
    record.msg_type = msg_type
    record.send_type = rule.send_type
    record.gift_type = rule.gift_type

    description = ''
    if introduced_by:
        description = u'【邀请人获得】'
    description = ''.join([description, msg_content])

    record.description = description
    record.save()


def _send_message_sms(user, rule, user_introduced_by=None, reward=None, amount=0):
    """
        inviter: 邀请人
        invited： 被邀请人
    """
    title = rule.rule_name
    mobile = user.wanglibaouserprofile.phone
    inviter_phone, invited_phone, reward_content = '', '', ''
    end_date, name, highest_amount = '', rule.rule_name, ''
    if reward:
        reward_content = reward.content
        fmt_str = "%Y年%m月%d日"
        end_date = timezone.localtime(reward.end_time).strftime(fmt_str)
        name = reward.type
    if rule.redpack:
        red_pack = RedPackEvent.objects.filter(id=int(rule.redpack)).first()
        if red_pack:
            highest_amount = red_pack.highest_amount
            name = red_pack.name
    if user_introduced_by:
        msg_template = rule.msg_template_introduce
        sms_template = rule.sms_template_introduce
        inviter_phone = safe_phone_str(user_introduced_by.wanglibaouserprofile.phone)
        invited_phone = safe_phone_str(mobile)
        context = Context({
            'mobile': safe_phone_str(mobile),
            'reward': reward_content,
            'inviter': inviter_phone,
            'invited': invited_phone,
            'income': rule.income,
            'amount': amount,
            'end_date': end_date,
            'name': name,
            'highest_amount': highest_amount
        })
        if msg_template:
            msg = Template(msg_template)
            content = msg.render(context)
            _send_message_template(user_introduced_by, title, content)
            _save_activity_record(rule, user_introduced_by, 'message', content, True)
        if sms_template:
            sms = Template(sms_template)
            content = sms.render(context) + u'回复TD退订 4008-588-066【网利宝】'
            _send_sms_template(user_introduced_by.wanglibaouserprofile.phone, content)
            _save_activity_record(rule, user_introduced_by, 'sms', content, True)
    else:
        msg_template = rule.msg_template
        sms_template = rule.sms_template
        invited_phone = safe_phone_str(mobile)
        introduced_by = IntroducedBy.objects.filter(user=user).first()
        if introduced_by and introduced_by.introduced_by:
            inviter_phone = safe_phone_str(introduced_by.introduced_by.wanglibaouserprofile.phone)
        context = Context({
            'mobile': invited_phone,
            'reward': reward_content,
            'inviter': inviter_phone,
            'invited': invited_phone,
            'income': rule.income,
            'amount': amount,
            'end_date': end_date,
            'name': name,
            'highest_amount': highest_amount
        })
        if msg_template:
            msg = Template(msg_template)
            content = msg.render(context)
            _send_message_template(user, title, content)
            _save_activity_record(rule, user, 'message', content)
        if sms_template:
            sms = Template(sms_template)
            content = sms.render(context) + u'回复TD退订 4008-588-066【网利宝】'
            _send_sms_template(mobile, content)
            _save_activity_record(rule, user, 'sms', content)


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

