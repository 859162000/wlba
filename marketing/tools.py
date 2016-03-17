#!/usr/bin/env python
# encoding:utf-8
from celery.utils.log import get_task_logger
import pytz

from wanglibao.celery import app
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from wanglibao_margin.models import Margin
from wanglibao_reward.models import WanglibaoUserGift
from wanglibao_p2p.models import P2PProduct
from wanglibao_account import message as inside_message
from wanglibao_sms import messages
from marketing.models import IntroducedBy
from marketing import utils
from wanglibao_sms.tasks import send_messages
from wanglibao_sms.send_php import PHPSendSMS
from wanglibao_redpack import backends as redpack_backends
from wanglibao_activity import backends as activity_backends
from wanglibao_redpack.models import Income, RedPackEvent, RedPack, RedPackRecord
import datetime
import json
from django.db.models import Sum, Count, Q
import logging
from django.conf import settings
from weixin.constant import DEPOSIT_SUCCESS_TEMPLATE_ID, WITH_DRAW_SUBMITTED_TEMPLATE_ID

from weixin.models import WeixinUser
from weixin.tasks import sentTemplate
from wanglibao_reward.tasks import sendWechatPhoneReward
from marketing.send_data import send_register_data, send_idvalidate_data, send_deposit_data, send_investment_data,\
     send_withdraw_data
from wanglibao_reward.utils import processMarchAwardAfterP2pBuy

# logger = logging.getLogger('wanglibao_reward')

logger = get_task_logger(__name__)

@app.task
def decide_first(user_id, amount, device, order_id, product_id=0, is_full=False):
    # fix@chenweibi, add order_id
    user = User.objects.filter(id=user_id).first()
    amount = long(amount)
    device_type = device['device_type']

    introduced_by = IntroducedBy.objects.filter(user=user).first()

    if introduced_by and introduced_by.bought_at is None:
        introduced_by.bought_at = timezone.now()
        introduced_by.save()

    # 活动检测
    activity_backends.check_activity(user, 'invest', device_type, amount, product_id, order_id, is_full)
    # fix@chenweibi, add order_id
    try:
        utils.log_clientinfo(device, "buy", user_id, order_id, amount)
    except Exception:
        pass
    # 发送红包
    # send_lottery.apply_async((user_id,))
    processMarchAwardAfterP2pBuy(user, product_id, order_id, amount)
    #往数据中心发送投资信息数据
    if settings.ENV == settings.ENV_PRODUCTION and settings.SEND_PHP_ON_OR_OFF:
        send_investment_data.apply_async(kwargs={
            "user_id": user_id, "amount": amount, "device_type":device_type,
            "order_id": order_id, "product_id": product_id,
        })
    if settings.ENV != settings.ENV_PRODUCTION and settings.SEND_PHP_ON_OR_OFF:
        send_investment_data.apply_async(kwargs={
            "user_id": user_id, "amount": amount, "device_type":device_type,
            "order_id": order_id, "product_id": product_id,
        })

def weixin_redpack_distribute(user):
    phone = user.wanglibaouserprofile.phone
    logger.info('通过weixin_redpack渠道注册,phone:%s' % (phone,))
    records = WanglibaoUserGift.objects.filter(valid=0, identity=phone)
    for record in records:
        try:
            redpack_backends.give_activity_redpack(user, record.rules.redpack, 'pc')
        except Exception, reason:
            logger.exception('Fail:注册的时候发送加息券失败, reason:%s' % (reason,))
        else:
            logger.info('Success:发送红包完毕,user:%s, redpack:%s' % (user, record.rules.redpack,))
        record.user = user
        record.valid = 1
        record.save()


@app.task
def register_ok(user_id, device):
    user = User.objects.filter(id=user_id).first()
    device_type = device['device_type']
    try:
        weixin_redpack_distribute(user)
    except Exception, reason:
        print reason
        pass
    title, content = messages.msg_register()
    inside_message.send_one.apply_async(kwargs={
        "user_id": user_id,
        "title": title,
        "content": content,
        "mtype": "activityintro"
    })
    # 活动检测
    activity_backends.check_activity(user, 'register', device_type)
    try:
        utils.log_clientinfo(device, "register", user_id)
    except Exception:
        pass
    sendWechatPhoneReward.apply_async(kwargs={
        "user_id": user_id,
    })
    #往数据中心发送注册信息数据
    if settings.ENV == settings.ENV_PRODUCTION and settings.SEND_PHP_ON_OR_OFF:
        send_register_data.apply_async(kwargs={
            "user_id": user_id, "device_type":device_type,
        })
    if settings.ENV != settings.ENV_PRODUCTION and settings.SEND_PHP_ON_OR_OFF:
        send_register_data.apply_async(kwargs={
            "user_id": user_id, "device_type":device_type,
        })

@app.task
def idvalidate_ok(user_id, device):
    user = User.objects.filter(id=user_id).first()
    device_type = device['device_type']

    # 活动检测
    activity_backends.check_activity(user, 'validation', device_type)
    try:
        utils.log_clientinfo(device, "validation", user_id)
    except Exception:
        pass
    #往数据中心发送实名信息数据
    if settings.ENV == settings.ENV_PRODUCTION and settings.SEND_PHP_ON_OR_OFF:
        if user.wanglibaouserprofile.id_is_valid:
            send_idvalidate_data.apply_async(kwargs={
                "user_id": user_id, "device_type":device_type,
            })
    if settings.ENV != settings.ENV_PRODUCTION and settings.SEND_PHP_ON_OR_OFF:
        if user.wanglibaouserprofile.id_is_valid:
            send_idvalidate_data.apply_async(kwargs={
                "user_id": user_id, "device_type":device_type,
            })
        
@app.task
def deposit_ok(user_id, amount, device, order_id):
    # fix@chenweibi, add order_id
    try:
        try:
            # 支持通过字典传递完整的device信息或是通过str直接传device_type
            if isinstance(device, dict):
                device_type = device['device_type']
            elif isinstance(device, str) or isinstance(device, unicode):
                assert device in ['pc', 'ios', 'android']
                device_type = device
            else:
                raise
        except:
            device_type = u'pc'
            logger.exception("=deposit_ok= Failed to get device_type")

        title, content = messages.msg_pay_ok(amount)
        inside_message.send_one.apply_async(kwargs={
            "user_id": user_id,
            "title": title,
            "content": content,
            "mtype": "activityintro"
        })

        user = User.objects.get(id=user_id)
        user_profile = user.wanglibaouserprofile
        activity_backends.check_activity(user, 'recharge', device_type,
                                         amount, **{'order_id': order_id})
        try:
            # Add by hb on 2015-12-18 : add return value
            flag = utils.log_clientinfo(device, "deposit", user_id, order_id, amount)
            if not flag:
                raise Exception("Failed to log_clientinfo")
        except Exception, ex:
            logger.exception("=20151218= [%s] [%s] [%s] [%s] [%s]" % (ex, device, user_id, order_id, amount))
            pass

        send_messages.apply_async(kwargs={
            'phones': [user_profile.phone],
            'messages': [messages.deposit_succeed(user_profile.name, amount)]
        })

        weixin_user = WeixinUser.objects.filter(user=user).first()
# 亲爱的满先生，您的充值已成功
# {{first.DATA}} 充值时间：{{keyword1.DATA}} 充值金额：{{keyword2.DATA}} 可用余额：{{keyword3.DATA}} {{remark.DATA}}
        if weixin_user:

            deposit_ok_time = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
            margin = Margin.objects.filter(user=user).first()
            sentTemplate.apply_async(kwargs={
                            "kwargs":json.dumps({
                                            "openid":weixin_user.openid,
                                            "template_id":DEPOSIT_SUCCESS_TEMPLATE_ID,
                                            "first":u"亲爱的%s，您的充值已成功"%user_profile.name,
                                            "keyword1":deposit_ok_time,
                                            "keyword2":"%s 元"%str(amount),
                                            "keyword3":str(margin.margin),
                                                })},
                                            queue='celery02')

        logger.info('=deposit_ok= Success: [%s], [%s], [%s]' % (user_profile.phone, order_id, amount))
    except Exception, e:
        logger.exception('=deposit_ok= Except: [%s]' % str(e))

    #往数据中心发送冲值信息数据
    if settings.ENV == settings.ENV_PRODUCTION and settings.SEND_PHP_ON_OR_OFF:
        send_deposit_data.apply_async(kwargs={
            "user_id": user_id, "amount": amount, "device_type":device_type, "order_id": order_id,
        })
    if settings.ENV != settings.ENV_PRODUCTION and settings.SEND_PHP_ON_OR_OFF:
        send_deposit_data.apply_async(kwargs={
            "user_id": user_id, "amount": amount, "device_type":device_type, "order_id": order_id,
        })
        
@app.task
def withdraw_submit_ok(user_id,user_name, phone, amount, bank_name, order_id, device):
    user = User.objects.filter(id=user_id).first()
    # 短信通知添加用户名
    try:
        # 支持通过字典传递完整的device信息或是通过str直接传device_type
        if isinstance(device, dict):
            device_type = device['device_type']
        elif isinstance(device, str) or isinstance(device, unicode):
            assert device in ['pc', 'ios', 'android']
            device_type = device
        else:
            raise
    except:
        device_type = u'pc'
        logger.exception("=withdraw_ok= Failed to get device_type")

    send_messages.apply_async(kwargs={
        'phones': [phone],
        # 'messages': [messages.withdraw_submitted(amount, timezone.now())]
        'messages': [messages.withdraw_submitted(user_name)]
    })
    title, content = messages.msg_withdraw(timezone.now(), amount)
    inside_message.send_one.apply_async(kwargs={
        "user_id": user.id,
        "title": title,
        "content": content,
        "mtype": "withdraw"
    })
    weixin_user = WeixinUser.objects.filter(user=user).first()
    if weixin_user:
        # 亲爱的{}，您的提现申请已受理，1-3个工作日内将处理完毕，请耐心等待。
    # {{first.DATA}} 取现金额：{{keyword1.DATA}} 到账银行：{{keyword2.DATA}} 预计到账时间：{{keyword3.DATA}} {{remark.DATA}}
        now = datetime.datetime.now()
        withdraw_ok_time = "%s前处理完毕"%(now+datetime.timedelta(days=3)).strftime('%Y年%m月%d日')
        sentTemplate.apply_async(kwargs={
                        "kwargs":json.dumps({
                                        "openid":weixin_user.openid,
                                        "template_id":WITH_DRAW_SUBMITTED_TEMPLATE_ID,
                                        "first":u"亲爱的%s，您的提现申请已受理"%user_name,
                                        "keyword1":"%s 元"%str(amount),
                                        "keyword2":bank_name,
                                        "keyword3":withdraw_ok_time,
                                        #"url":settings.CALLBACK_HOST + '/weixin/activity_ggl/',
                                            })},
                                        queue='celery02')

    try:
        utils.log_clientinfo(device, "withdraw", user_id, order_id, amount)
    except Exception:
        pass
    

    #往数据中心发送提现信息数据
    if settings.ENV == settings.ENV_PRODUCTION and settings.SEND_PHP_ON_OR_OFF:
        send_withdraw_data.apply_async(kwargs={
            "user_id": user_id, "amount": amount, "order_id": order_id, "device_type":device_type,
        })
    if settings.ENV != settings.ENV_PRODUCTION and settings.SEND_PHP_ON_OR_OFF:
        send_withdraw_data.apply_async(kwargs={
            "user_id": user_id, "amount": amount, "order_id": order_id, "device_type":device_type,
        })

@app.task
def calc_broker_commission(product_id):
    if not product_id:
        return

    product = P2PProduct.objects.filter(id=product_id).first()
    _method = product.pay_method
    _period = product.period
    if _method.startswith(u"日计息") and _period <= 61 or _period <=2:
        return
    if redpack_backends.commission_exist(product):
        return

    start = timezone.datetime(2015, 6, 22, 16, 0, 0, tzinfo=timezone.utc)
    end = timezone.datetime(2016, 6, 30, 15, 59, 59, tzinfo=timezone.utc)
    with transaction.atomic():
        for equity in product.equities.all():
            redpack_backends.commission(equity.user, product, equity.equity, start, end)


@app.task
def send_income_message_sms():
    today = datetime.datetime.now()
    yestoday = today - datetime.timedelta(days=1)
    start = timezone.datetime(yestoday.year, yestoday.month, yestoday.day, 20, 0, 0)
    end = timezone.datetime(today.year, today.month, today.day, 20, 0, 0)
    incomes = Income.objects.filter(created_at__gte=start, created_at__lt=end).values('user')\
                            .annotate(Count('invite', distinct=True)).annotate(Sum('earning'))
    phones_list = []
    messages_list = []
    if incomes:
        # i = 0
        # data_messages = {}
        for income in incomes:
            user_info = User.objects.filter(id=income.get('user'))\
                .select_related('user__wanglibaouserprofile')\
                .values('wanglibaouserprofile__phone', 'wanglibaouserprofile__name').first()
            phone = user_info.get('wanglibaouserprofile__phone')
            name = user_info.get('wanglibaouserprofile__name')
            if not name:
                from wanglibao.templatetags.formatters import safe_phone_str
                name = safe_phone_str(phone)

            # data_messages[i] = {
            #     'user_id': phone,
            #     'user_type': 'phone',
            #     'params': {
            #         'name': name,
            #         'count': int(income.get('invite__count')),
            #         'amount': float(income.get('earning__sum'))
            #     }
            # }
            # i += 1
            phones_list.append(phone)
            messages_list.append(messages.sms_income(name,
                                                     income.get('invite__count'),
                                                     income.get('earning__sum')))

            # 发送站内信
            title, content = messages.msg_give_income(income.get('invite__count'), income.get('earning__sum'))
            inside_message.send_one.apply_async(kwargs={
                "user_id": income.get('user'),
                "title": title,
                "content": content,
                "mtype": "invite"
            })

        # 批量发送短信
        # 功能推送id: 3
        # PHPSendSMS().send_sms(rule_id=3, data_messages=data_messages)
        send_messages.apply_async(kwargs={
            "phones": phones_list,
            "messages": messages_list,
        })


@app.task
def check_unavailable_3_days():
    """
    每天一次检查3天后到期的红包优惠券.发短息提醒投资.
    直接用sql语句查询。
    分两种情况查询,1为查询理财券活动的截止日期,2为查询动态截止日期的
    """
    from django.db import connection
    # 查询三天后的日期
    days = 3
    check_date = timezone.now() + timezone.timedelta(days=days)
    start_date = utils.local_to_utc(check_date, 'min').strftime('%Y-%m-%d %H:%M:%S')
    end_date = utils.local_to_utc(check_date, 'max').strftime('%Y-%m-%d %H:%M:%S')

    cursor = connection.cursor()

    sql = "SELECT COUNT(a.user_id), a.user_id, b.phone FROM " \
          "(SELECT r.user_id, e.auto_extension AS is_auto, e.unavailable_at, " \
          "DATE_ADD(r.created_at, INTERVAL e.auto_extension_days day) end_date " \
          "FROM wanglibao_redpack_redpackrecord AS r, " \
          "wanglibao_redpack_redpack AS p, " \
          "wanglibao_redpack_redpackevent AS e " \
          "WHERE r.redpack_id = p.id AND p.event_id = e.id and r.order_id is NULL) AS a, " \
          "wanglibao_profile_wanglibaouserprofile AS b " \
          "WHERE a.user_id = b.user_id " \
          "AND ((a.is_auto = 0 AND a.unavailable_at > '{}' AND a.unavailable_at <= '{}') " \
          "OR (a.is_auto = 1 AND a.end_date > '{}' AND a.end_date <= '{}')) " \
          "GROUP BY a.user_id;".format(start_date, end_date, start_date, end_date)

    cursor.execute(sql)
    fetchall = cursor.fetchall()

    data_messages = {}
    for idx, item in enumerate(fetchall):
        data_messages[idx] = {
            'user_id': item[2],
            'user_type': 'phone',
            'params': {
                'count': item[0],
                'days': days
            }
        }
    # 功能推送id: 1
    PHPSendSMS().send_sms(rule_id=1, data_messages=data_messages)


@app.task
def check_invested_status(delta=timezone.timedelta(days=3)):
    """
    每天一次检查3天没投资的用户.发短息提醒投资.
    """
    check_date = timezone.now() - delta
    start = timezone.datetime(year=check_date.year, month=check_date.month, day=check_date.day).replace(tzinfo=pytz.UTC)
    end = start + timezone.timedelta(days=1)

    # 三天前注册的用户
    registered_users = User.objects.filter(date_joined__gte=start, date_joined__lt=end)
    # 获取投资过的uid
    margins = Margin.objects.filter(user__in=registered_users, margin__gt=0).annotate(Count('user', distinct=True))
    ids = [margin.user.id for margin in margins]

    # 获取没有投资的用户
    users = registered_users.exclude(id__in=ids)

    data_messages = {}
    i = 0
    for user in users:
        data_messages[i] = {
            'user_id': user.wanglibaouserprofile.phone,
            'user_type': 'phone',
            'params': {}
        }
        i += 1

    # 功能推送id: 2
    PHPSendSMS().send_sms(rule_id=2, data_messages=data_messages)

    # phones_list = []
    # for user in users:
    #     try:
    #         phones_list.append(user.wanglibaouserprofile.phone)
    #     except Exception, e:
    #         print e
    #         pass
    # send_messages.apply_async(kwargs={
    #     'phones': phones_list,
    #     'messages': [messages.user_invest_alert()],
    #     'ext': 666,  # 营销类短信发送必须增加ext参数,值为666
    # })


@app.task
def check_and_generate_codes():
    from marketing.mock_generator import MockGenerator
    generate = MockGenerator()
    generate.check_and_generate_codes()


# def send_message_to_all():
#     all_users = User.objects.all().values('id')
#     count = 0
#     for user in all_users:
#         user_id = user.get('id')
#
#         title = u'七夕有礼 好事成双'
#         content = u'【七夕有礼 好事成双】活动：通过APP注册就送10元现金红包；通过APP首次投资满1000元，送20元现金红包。活动有效期：2015年8月18日 — 2015年8月21日。'
#
#         inside_message.send_one.apply_async(kwargs={
#             "user_id": user_id,
#             "title": title,
#             "content": content,
#             "mtype": "activityintro"
#         })
#
#         count += 1
#
#         if count % 1000 == 0:
#             time.sleep(30)
#
#     return count
