# encoding:utf-8

import time
import datetime
import json
import logging
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q, Sum
from django.db import transaction
from django.contrib.auth.models import User
from django.template import Template, Context
from models import Activity, ActivityRule, ActivityRecord
from marketing import helper
from marketing.models import IntroducedBy, Reward, RewardRecord
from wanglibao_redpack import backends as redpack_backends
from wanglibao_redpack.models import RedPackEvent, RedPack, RedPackRecord
from wanglibao_pay.models import PayInfo
from wanglibao_p2p.models import P2PRecord, P2PEquity
from wanglibao_account import message as inside_message
from wanglibao.templatetags.formatters import safe_phone_str
from wanglibao_sms.tasks import send_messages
from wanglibao_rest.utils import decide_device
from experience_gold.models import ExperienceEvent, ExperienceEventRecord
from weixin.models import WeixinUser
from weixin.constant import BIND_SUCCESS_TEMPLATE_ID
from weixin.tasks import sentTemplate

logger = logging.getLogger(__name__)


def check_activity(user, trigger_node, device_type, amount=0, product_id=0, order_id=0, is_full=False, is_first_bind=False):
    now = timezone.now()
    device_type = decide_device(device_type)
    if not trigger_node:
        return
    channel = helper.which_channel(user)
    #查询符合条件的活动
    # TODO: 需要将渠道的判断的范围从渠道name缩小为渠道code
    activity_list = Activity.objects.filter(start_at__lt=now, end_at__gt=now, is_stopped=False)\
                                    .filter(Q(platform=device_type) | Q(platform=u'all')).order_by('-id')
    if activity_list:
        for activity in activity_list:
            if activity.is_all_channel is False and trigger_node not in ('p2p_audit', 'repaid'):
                if activity.channel != "":
                    channel_list = activity.channel.split(",")
                    channel_list = [ch for ch in channel_list if ch.strip() != ""]
                    if channel not in channel_list:
                        continue
            # 查询活动规则
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
                            _check_rules_trigger(user, rule, rule.trigger_node, device_type,
                                                 amount, product_id, is_full, order_id, user_ib, is_first_bind_wx=is_first_bind)
                    else:
                        _check_rules_trigger(user, rule, rule.trigger_node, device_type,
                                             amount, product_id, is_full, order_id, is_first_bind_wx=is_first_bind)
            else:
                continue
    else:
        return


def _check_rules_trigger(user, rule, trigger_node, device_type, amount, product_id, is_full, order_id, user_ib=None, is_first_bind_wx=False):
    """ check the trigger node """
    product_id = int(product_id)
    order_id = int(order_id)
    # 注册 或 实名认证
    if trigger_node in ('register', 'validation'):
        _send_gift(user, rule, device_type, is_full)
    # 首次充值
    elif trigger_node == 'first_pay':
        # check first pay
        penny = Decimal(0.01).quantize(Decimal('.01'))
        with transaction.atomic():
            # 等待pay_info交易完成
            pay_info_lock = PayInfo.objects.select_for_update().get(order_id=order_id)
        if rule.is_in_date:
            first_pay = PayInfo.objects.filter(user=user, type='D', amount__gt=penny,
                                               update_time__gt=rule.activity.start_at,
                                               status=PayInfo.SUCCESS
                                               ).order_by('create_time').first()
        else:
            first_pay = PayInfo.objects.filter(user=user, type='D', amount__gt=penny,
                                               status=PayInfo.SUCCESS
                                               ).order_by('create_time').first()

        if first_pay and int(first_pay.order_id) == int(order_id):
            # Add by hb only for debug
            if first_pay.order_id <> order_id:
                logger.exception("=_check_rules_trigger= first_pay: type(%s)=[%s], type(%s)=[%s]" % (first_pay.order_id, type(first_pay.order_id), order_id, type(order_id)))
            _check_trade_amount(user, rule, device_type, amount, is_full)
        else:
            # Add by hb only for debug
            order_pay = PayInfo.objects.filter(order_id=int(order_id)).first()
            if order_pay:
                logger.error("=_check_rules_trigger= first_pay: order_id=[%s], status=[%s], amount=[%s]" % (order_id, order_pay.status, order_pay.amount))
            else:
                logger.error("=_check_rules_trigger= first_pay: order_id=[%s] not found" % (order_id))

    # 充值
    elif trigger_node == 'pay':
        _check_trade_amount(user, rule, device_type, amount, is_full)
    # 首次购买
    elif trigger_node == 'first_buy':
        # check first pay
        if rule.is_in_date:
            first_buy = P2PRecord.objects.filter(user=user,
                                                 create_time__gt=rule.activity.start_at
                                                 ).order_by('create_time').first()
        else:
            first_buy = P2PRecord.objects.filter(user=user
                                                 ).order_by('create_time').first()

        if first_buy and int(first_buy.order_id) == int(order_id):
            # Add by hb only for debug
            if first_buy.order_id <> order_id:
                logger.exception("=_check_rules_trigger= first_buy: type(%s)=[%s], type(%s)=[%s]" % (first_buy.order_id, type(first_buy.order_id), order_id, type(order_id)))
            # 判断当前购买产品id是否在活动设置的id中
            if product_id > 0 and rule.activity.product_ids:
                is_product = _check_product_id(product_id, rule.activity.product_ids)
                if is_product:
                    _check_buy_product(user, rule, device_type, amount, product_id, is_full)
            else:
                _check_buy_product(user, rule, device_type, amount, product_id, is_full)

    # 购买
    elif trigger_node == 'buy':
        if product_id > 0 and rule.activity.product_ids:
            is_product = _check_product_id(product_id, rule.activity.product_ids)
            if is_product:
                _check_buy_product(user, rule, device_type, amount, product_id, is_full)
        else:
            _check_buy_product(user, rule, device_type, amount, product_id, is_full)
    # 满标审核

    # 满标审核时,是给所有的持仓用户发放奖励,金额为持仓金额

    elif trigger_node == 'p2p_audit':
        # 根据product_id查询出该产品中所有的持仓用户,因为持仓确认是通过任务定时执行的,因此此处不查询confirm=True
        if product_id > 0:
            if rule.activity.product_ids:
                # 检查产品是否符合条件
                is_product = _check_product_id(product_id, rule.activity.product_ids)
                if is_product:
                    equities = P2PEquity.objects.filter(product=product_id)
                    if equities:
                        for equity in equities:
                            # 检查持仓金额是否满足
                            is_amount = _check_amount(rule.min_amount, rule.max_amount, equity.equity)
                            if is_amount:
                                _send_gift(equity.user, rule, device_type, is_full, equity.equity)
            else:
                equities = P2PEquity.objects.filter(product=product_id)
                if equities:
                    for equity in equities:
                        is_amount = _check_amount(rule.min_amount, rule.max_amount, equity.equity)
                        if is_amount:
                            _send_gift(equity.user, rule, device_type, is_full, equity.equity)
    # 还款

    # 还款时,是给所有的持仓用户发放奖励,金额为还款本金
    elif trigger_node == 'repaid':
        if product_id > 0:
            if rule.activity.product_ids:
                is_product = _check_product_id(product_id, rule.activity.product_ids)
                if is_product:
                    # 检查还款本金是否满足
                    is_amount = _check_amount(rule.min_amount, rule.max_amount, amount)
                    if is_amount:
                        _send_gift(user, rule, device_type, is_full, amount)
            else:
                is_amount = _check_amount(rule.min_amount, rule.max_amount, amount)
                if is_amount:
                    _send_gift(user, rule, device_type, is_full, amount)
    elif trigger_node == 'first_bind_weixin':
        if is_first_bind_wx:
            _send_gift(user, rule, device_type, is_full)
    else:
        return

def _send_gift(user, rule, device_type, is_full, amount=0):
    # rule_id = rule.id
    rtype = rule.trigger_node
    # 送奖品
    if rule.gift_type == 'reward':
        reward_name = rule.reward
        _send_gift_reward(user, rule, rtype, reward_name, device_type, amount, is_full)

    # 送优惠券，红包
    if rule.gift_type == 'redpack':
        redpack_id = rule.redpack
        # 此处后期要加上检测红包数量的逻辑，数量不够就记录下没有发送的用户，并通知市场相关人员
        _send_gift_redpack(user, rule, rtype, redpack_id, device_type, amount, is_full)

    # 送体验金
    if rule.gift_type == 'experience_gold':
        experience_id = rule.redpack
        _send_gift_experience(user, rule, rtype, experience_id, device_type, amount, is_full)

    # 送现金或收益
    # if rule.gift_type == 'income':
    #     send to
    #     _send_gift_income(user, rule, amount, is_full)

    # 送话费
    # if rule.gift_type == 'phonefare':
    #     send to
    #     _send_gift_phonefare(user, rule, amount, is_full)


def _check_introduced_by(user, start_dt, is_invite_in_date):
    if is_invite_in_date:
        ib = IntroducedBy.objects.filter(user=user, created_at__gt=start_dt).first()
    else:
        ib = IntroducedBy.objects.filter(user=user).first()

    if ib:
        return ib.introduced_by
    else:
        return None


def _check_introduced_by_product(user):
    ib = IntroducedBy.objects.filter(user=user).first()

    if ib:
        return ib.product_id
    else:
        return None


def _check_buy_product(user, rule, device_type, amount, product_id, is_full):
    # 检查单标投资顺序是否设置数字
    ranking_num = int(rule.ranking)
    if not rule.is_total_invest:
        if ranking_num > 0 and not is_full:
            # 查询单标投资顺序
            records = P2PRecord.objects.filter(product=product_id, catalog=u'申购') \
                                       .order_by('create_time')
            print records.query
            if records and records.count() <= ranking_num:
                try:
                    this_record = records[ranking_num-1]
                    if this_record.user.id == user.id:
                        _check_trade_amount(user, rule, device_type, amount, is_full)
                        # _send_gift(user, rule, device_type, is_full)
                except Exception:
                    pass
        if ranking_num > 0 and is_full is True:
            # 符合抢标顺序且满标
            records = P2PRecord.objects.filter(product=product_id, catalog=u'申购') \
                                       .order_by('create_time')
            # print records.query
            if records and records.count() <= ranking_num:
                try:
                    this_record = records[ranking_num-1]
                    if this_record.user.id == user.id:
                        _check_trade_amount(user, rule, device_type, amount, is_full)
                except Exception:
                    pass
        elif ranking_num == -1 and is_full is True:
            # 查询是否满标，满标时不再考虑最小/最大金额，直接发送
            _check_trade_amount(user, rule, device_type, amount, is_full)
            # _send_gift(user, rule, device_type, is_full)
        elif ranking_num == 0 and not is_full:
            _check_trade_amount(user, rule, device_type, amount, is_full)

    # 判断单标累计投资名次
    if rule.is_total_invest and is_full is True:
        total_invest_order = int(rule.total_invest_order)
        if total_invest_order > 0:
            # 按用户查询单标投资的总金额
            records = P2PEquity.objects.filter(product=product_id, product__status=u'满标待打款').order_by('-equity')
            if records:
                try:
                    record = records[total_invest_order-1]
                    # 如果设置了最小金额，则判断用户的投资总额是否在最大最小金额区间
                    is_amount = _check_amount(rule.min_amount, rule.max_amount, record.equity)
                    if is_amount:
                        _send_gift(record.user, rule, device_type, is_full)
                except Exception:
                    pass


def _check_trade_amount(user, rule, device_type, amount, is_full):
    is_amount = _check_amount(rule.min_amount, rule.max_amount, amount)
    if amount and amount > 0:
        if is_amount:
            _send_gift(user, rule, device_type, is_full, amount)
    else:
        _send_gift(user, rule, device_type, is_full, amount)


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


def _send_gift_reward(user, rule, rtype, reward_name, device_type, amount, is_full):
    now = timezone.now()
    if rule.send_type == 'sys_auto':
        # do send
        if rule.share_type != 'inviter':
            _send_reward(user, rule, rtype, reward_name, None, amount)
        if rule.share_type == 'both' or rule.share_type == 'inviter':
            user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
            if user_introduced_by:
                _send_reward(user, rule, rtype, reward_name, user_introduced_by, amount)
    else:
        # 只记录不发信息
        if rule.share_type != 'inviter':
            _save_activity_record(rule, user, 'only_record', reward_name, False, is_full)
        if rule.share_type == 'both' or rule.share_type == 'inviter':
            user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
            if user_introduced_by:
                _save_activity_record(rule, user_introduced_by, 'only_record', reward_name, True, is_full)


def _send_reward(user, rule, rtype, reward_name, user_introduced_by=None, amount=0):
    now = timezone.now()
    reward = Reward.objects.filter(type=reward_name,
                                   is_used=False,
                                   end_time__gte=now).first()
    if reward:
        reward.is_used = True
        reward.save()
        description = '=>'.join([rtype, reward.type])
        # 记录奖品发放流水
        has_reward_record = _keep_reward_record(user, reward, description)
        if has_reward_record:
            # 发放站内信或短信
            if user_introduced_by:
                _send_message_sms(user, rule, user_introduced_by, reward, amount)
            else:
                _send_message_sms(user, rule, None, reward, amount)


def _send_gift_income(user, rule, amount, is_full):
    # now = timezone.now()
    income = rule.income
    if income > 0:
        if rule.send_type == 'sys_auto':
            if rule.share_type != 'inviter':
                _send_message_sms(user, rule, None, None, amount)
            if rule.share_type == 'both' or rule.share_type == 'inviter':
                user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
                if user_introduced_by:
                    _send_message_sms(user, rule, user_introduced_by, None, amount)
        else:
            #只记录不发信息
            if rule.share_type != 'inviter':
                _save_activity_record(rule, user, 'only_record', rule.rule_name, False, is_full)
            if rule.share_type == 'both' or rule.share_type == 'inviter':
                user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
                if user_introduced_by:
                    _save_activity_record(rule, user_introduced_by, 'only_record', rule.rule_name, True, is_full)
    else:
        return


def _send_gift_phonefare(user, rule, amount, is_full):
    # now = timezone.now()
    phone_fare = rule.income
    if phone_fare > 0:
        if rule.send_type == 'sys_auto':
            if rule.share_type != 'inviter':
                _send_message_sms(user, rule, None, None, amount)
            if rule.share_type == 'both' or rule.share_type == 'inviter':
                user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
                if user_introduced_by:
                    _send_message_sms(user, rule, user_introduced_by, None, amount)
        else:
            #只记录不发信息
            if rule.share_type != 'inviter':
                _save_activity_record(rule, user, 'only_record', rule.rule_name, False, is_full)
            if rule.share_type == 'both' or rule.share_type == 'inviter':
                user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
                if user_introduced_by:
                    _save_activity_record(rule, user_introduced_by, 'only_record', rule.rule_name, True, is_full)
    else:
        return


def _send_gift_redpack(user, rule, rtype, redpack_id, device_type, amount, is_full):
    """ 活动中发送的红包使用规则里边配置的模板，其他的使用系统原有的模板。 """
    if rule.send_type == 'sys_auto':
        if rule.share_type != 'inviter':
            _give_activity_redpack_new(user, rtype, redpack_id, device_type, rule, None, amount)
        if rule.share_type == 'both' or rule.share_type == 'inviter':
            user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
            #logger.info("user_introduced_by %s" % user_introduced_by)
            if user_introduced_by:
                _give_activity_redpack_new(user, rtype, redpack_id, device_type, rule, user_introduced_by, amount)
    else:
        if rule.share_type != 'inviter':
            _save_activity_record(rule, user, 'only_record', rule.rule_name, False, is_full)
        if rule.share_type == 'both' or rule.share_type == 'inviter':
            user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
            if user_introduced_by:
                _save_activity_record(rule, user_introduced_by, 'only_record', rule.rule_name, True, is_full)


def _give_activity_redpack_new(user, rtype, redpack_id, device_type, rule, user_ib=None, amount=0):
    # add by hb for debug
    try:
        phone = user.wanglibaouserprofile.phone
    except:
        phone = None
    logger.debug("=_give_activity_redpack_new= [%s], [%s], [%s], [%s], [%s], [%s], [%s]" % (phone, rtype, redpack_id, device_type, rule, user_ib, amount))
    print("=_give_activity_redpack_new= [%s], [%s], [%s], [%s], [%s], [%s], [%s]" % (phone, rtype, redpack_id, device_type, rule, user_ib, amount))
    """ rule: get message template """
    now = timezone.now()
    if user_ib:
        this_user = user_ib
    else:
        this_user = user
    user_channel = helper.which_channel(this_user)
    device_type = decide_device(device_type)

    # 新增允许一次填写多个优惠券ID号
    if redpack_id:
        redpack_id_list = redpack_id.split(',')
        redpack_id_list = [int(rid) for rid in redpack_id_list if rid.strip() != '']
    else:
        return

    #print redpack_id_list
    if len(redpack_id_list) == 1:
        #print(redpack_id_list[0])
        red_pack_event = RedPackEvent.objects.filter(give_mode=rtype, invalid=False, id=redpack_id_list[0],
                                                     give_start_at__lt=now, give_end_at__gt=now).first()
        if red_pack_event:
            if red_pack_event.target_channel != "":
                chs = red_pack_event.target_channel.split(",")
                chs = [m for m in chs if m.strip() != ""]
                if user_channel not in chs:
                    return
            redpack = RedPack.objects.filter(event=red_pack_event, status="unused").first()
            if redpack:
                # event = redpack.event
                give_pf = red_pack_event.give_platform
                if give_pf == "all" or give_pf == device_type or (give_pf == 'app' and device_type in ('ios', 'android')):
                    if redpack.token != "":
                        redpack.status = "used"
                        redpack.save()
                    record = RedPackRecord()
                    record.user = this_user
                    record.redpack = redpack
                    record.change_platform = device_type
                    record.save()
                    if user_ib:
                        _send_message_sms(user, rule, user_ib, None, amount, red_pack_event, record.created_at)
                    else:
                        _send_message_sms(user, rule, None, None, amount, red_pack_event, record.created_at)
    else:
        for red_pack_id in redpack_id_list:
            red_pack_event = RedPackEvent.objects.filter(give_mode=rtype, invalid=False, id=red_pack_id,
                                                         give_start_at__lt=now, give_end_at__gt=now).first()
            if red_pack_event:
                if red_pack_event.target_channel != "":
                    chs = red_pack_event.target_channel.split(",")
                    chs = [m for m in chs if m.strip() != ""]
                    if user_channel not in chs:
                        continue
                redpack = RedPack.objects.filter(event=red_pack_event, status="unused").first()
                if redpack:
                    give_pf = red_pack_event.give_platform
                    if give_pf == "all" or give_pf == device_type or (give_pf == 'app' and device_type in ('ios', 'android')):
                        if redpack.token != "":
                            redpack.status = "used"
                            redpack.save()
                        record = RedPackRecord()
                        record.user = this_user
                        record.redpack = redpack
                        record.change_platform = device_type
                        record.save()
        if user_ib:
            _send_message_sms(user, rule, user_ib, None, amount, None, None)
        else:
            _send_message_sms(user, rule, None, None, amount, None, None)


def _send_gift_experience(user, rule, rtype, experience_id, device_type, amount, is_full):
    """ 活动中发送的理财金使用规则里边配置的模板，其他的使用系统原有的模板。 """
    if rule.send_type == 'sys_auto':
        if rule.share_type != 'inviter':
            _give_activity_experience_new(user, rtype, experience_id, device_type, rule, None, amount)
        if rule.share_type == 'both' or rule.share_type == 'inviter':
            user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
            if user_introduced_by:
                _give_activity_experience_new(user, rtype, experience_id, device_type, rule, user_introduced_by, amount)
    else:
        if rule.share_type != 'inviter':
            _save_activity_record(rule, user, 'only_record', rule.rule_name, False, is_full)
        if rule.share_type == 'both' or rule.share_type == 'inviter':
            user_introduced_by = _check_introduced_by(user, rule.activity.start_at, rule.is_invite_in_date)
            if user_introduced_by:
                _save_activity_record(rule, user_introduced_by, 'only_record', rule.rule_name, True, is_full)


def _give_activity_experience_new(user, rtype, experience_id, device_type, rule, user_ib=None, amount=0):
    """ rule: get message template """
    now = timezone.now()
    if user_ib:
        this_user = user_ib
    else:
        this_user = user
    user_channel = helper.which_channel(this_user)
    device_type = decide_device(device_type)

    # 新增允许一次填写多个体验金ID号
    if experience_id:
        experience_id_list = experience_id.split(',')
        experience_id_list = [int(rid) for rid in experience_id_list if rid.strip() != '']
    else:
        return

    # 限制id为1的体验金重复发放
    experience_count = ExperienceEventRecord.objects.filter(user=user).filter(event__id=1).count()
    if experience_count:
        logger.debug(">>>>用户id: {}, ID为1的体验金已经发放过,不允许重复领取".format(user.id))
        return

    if len(experience_id_list) == 1:
        experience_event = ExperienceEvent.objects.filter(give_mode=rtype, invalid=False, id=experience_id_list[0],
                                                          available_at__lt=now, unavailable_at__gt=now).first()
        if experience_event:
            if experience_event.target_channel != "":
                chs = experience_event.target_channel.split(",")
                chs = [m for m in chs if m.strip() != ""]
                if user_channel not in chs:
                    return

            give_pf = experience_event.give_platform
            if give_pf == "all" or give_pf == device_type or (give_pf == 'app' and device_type in ('ios', 'android')):
                record = ExperienceEventRecord()
                record.event = experience_event
                record.user = this_user
                record.save()
                if user_ib:
                    _send_message_sms(user, rule, user_ib, None, amount)
                else:
                    _send_message_sms(user, rule, None, None, amount)
    else:
        for e_id in experience_id_list:
            experience_event = ExperienceEvent.objects.filter(give_mode=rtype, invalid=False, id=e_id,
                                                              available_at__lt=now, unavailable_at__gt=now).first()
            if experience_event:
                if experience_event.target_channel != "":
                    chs = experience_event.target_channel.split(",")
                    chs = [m for m in chs if m.strip() != ""]
                    if user_channel not in chs:
                        continue

                give_pf = experience_event.give_platform
                if give_pf == "all" or give_pf == device_type or (give_pf == 'app' and device_type in ('ios', 'android')):
                    record = ExperienceEventRecord()
                    record.event = experience_event
                    record.user = this_user
                    record.save()
        if user_ib:
            _send_message_sms(user, rule, user_ib, None, amount)
        else:
            _send_message_sms(user, rule, None, None, amount)


def _save_activity_record(rule, user, msg_type, msg_content='', introduced_by=False, is_full=False):
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

    description, total_order, ranking = '', '', ''
    if introduced_by:
        description = u'【邀请人获得】'
    if rule.total_invest_order > 0 and is_full is True:
        total_order = u'【满标累计投资第%d名】' % rule.total_invest_order
    if rule.ranking > 0:
        ranking = u'【第%d名投资】' % rule.ranking
    description = ''.join([description, ranking, total_order, msg_content])

    record.description = description
    record.save()


def _send_message_sms(user, rule, user_introduced_by=None, reward=None, amount=0, redpack_event=None, created_at=None, is_first_bind_wx=False):
    """
        inviter: 邀请人
        invited： 被邀请人
    """
    title = rule.rule_name
    mobile = user.wanglibaouserprofile.phone
    inviter_phone, invited_phone, reward_content = '', '', ''
    end_date, name, highest_amount, redpack_amount, invest_amount = '', rule.rule_name, '', '', ''
    fmt_str = "%Y年%m月%d日"
    if reward:
        reward_content = reward.content
        end_date = timezone.localtime(reward.end_time).strftime(fmt_str)
        name = reward.type
    if redpack_event:
        try:
            redpack_amount = redpack_event.amount
        except AttributeError:
            redpack_amount = 0
        try:
            invest_amount = redpack_event.invest_amount
        except AttributeError:
            invest_amount = 0
        try:
            highest_amount = redpack_event.highest_amount
        except AttributeError:
            highest_amount = 0
        name = redpack_event.name
        if redpack_event.auto_extension and redpack_event.auto_extension_days > 0 and created_at:
            unavailable_at = created_at + datetime.timedelta(days=int(redpack_event.auto_extension_days))
            # if unavailable_at < redpack_event.unavailable_at:
            #     unavailable_at = redpack_event.unavailable_at
        else:
            unavailable_at = redpack_event.unavailable_at
        end_date = timezone.localtime(unavailable_at).strftime(fmt_str)
    context = Context({
        'mobile': safe_phone_str(mobile),
        'reward': reward_content,
        'income': rule.income,
        'amount': amount,
        'end_date': end_date,
        'name': name,
        'redpack_amount': redpack_amount,
        'invest_amount': invest_amount,
        'highest_amount': highest_amount
    })

    if user_introduced_by:
        msg_template = rule.msg_template_introduce
        sms_template = rule.sms_template_introduce
        inviter_phone = safe_phone_str(user_introduced_by.wanglibaouserprofile.phone)
        invited_phone = safe_phone_str(mobile)
        context.update({
            'inviter': inviter_phone,
            'invited': invited_phone,
        })
        if msg_template:
            msg = Template(msg_template)
            content = msg.render(context)
            _send_message_template(user_introduced_by, title, content)
            _save_activity_record(rule, user_introduced_by, 'message', content, True)
        if sms_template:
            sms = Template(sms_template)
            content = sms.render(context)
            _send_sms_template(user_introduced_by.wanglibaouserprofile.phone, content)
            _save_activity_record(rule, user_introduced_by, 'sms', content, True)
    else:
        msg_template = rule.msg_template
        sms_template = rule.sms_template
        wx_template = rule.wx_template
        invited_phone = safe_phone_str(mobile)
        introduced_by = IntroducedBy.objects.filter(user=user).first()
        if introduced_by and introduced_by.introduced_by:
            inviter_phone = safe_phone_str(introduced_by.introduced_by.wanglibaouserprofile.phone)
        context.update({
            'inviter': inviter_phone,
            'invited': invited_phone,
        })
        if msg_template:
            msg = Template(msg_template)
            content = msg.render(context)
            _send_message_template(user, title, content)
            _save_activity_record(rule, user, 'message', content)
        if sms_template:
            sms = Template(sms_template)
            content = sms.render(context)
            _send_sms_template(mobile, content)
            _save_activity_record(rule, user, 'sms', content)
        if wx_template:
            if wx_template == "first_bind":
                _send_wx_frist_bind_template(user, end_date, redpack_amount, invest_amount)


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

def _send_wx_frist_bind_template(user, end_date, amount, invest_amount):
    weixin_user = WeixinUser.objects.filter(user=user).first()
    if weixin_user:
        now_str = datetime.datetime.now().strftime('%Y年%m月%d日')
        remark = u"获赠红包：%s元\n起投金额：%s元\n有效期至：%s\n您可以使用下方微信菜单进行更多体验。"%(amount,
                                                                     invest_amount, end_date)
        sentTemplate.apply_async(kwargs={"kwargs":json.dumps({
                                    "openid":weixin_user.openid,
                                    "template_id":BIND_SUCCESS_TEMPLATE_ID,
                                    "name1":"",
                                    "name2":user.wanglibaouserprofile.phone,
                                    "time":now_str+'\n',
                                    "remark":remark
                                        })},
                                    queue='celery02'
                                    )

