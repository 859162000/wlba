#!/usr/bin/env python
# encoding:utf-8

from wanglibao.celery import app
from wanglibao_p2p.models import P2PProduct
from django.contrib.auth.models import User
import re
import json
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import datetime

from weixin.models import SubscribeRecord, SubscribeService, WeixinUser
from weixin.constant import MessageTemplate, PRODUCT_ONLINE_TEMPLATE_ID, BIND_SUCCESS_TEMPLATE_ID
from weixin.views import SendTemplateMessage
from wanglibao_redpack.models import RedPackRecord, RedPackEvent
from wanglibao_redpack.backends import get_start_end_time, local_transform_str,stamp


@app.task
def bind_ok(openid, is_first_bind, redpack_record_id):
    weixin_user = WeixinUser.objects.get(openid=openid)
    now_str = datetime.datetime.now().strftime('%Y年%m月%d日')
    if is_first_bind and redpack_record_id:
        redpack_record = RedPackRecord.objects.get(id=redpack_record_id)
        if redpack_record and redpack_record.user == weixin_user.user:
            # 获赠红包：20元
            # 起投金额：2000元
            # 有效期：**年**月**日（自领取之日起7天有效）
            redpack_event = redpack_record.redpack.event
            start_time, endtime = get_start_end_time(redpack_event.auto_extension, redpack_event.auto_extension_days,
                                              redpack_record.created_at, redpack_event.available_at, redpack_event.unavailable_at)
            remark = u"获赠红包：%s元\n起投金额：%s元\n有效期至：%s\n您可以使用下方微信菜单进行更多体验。"%(redpack_event.amount,
                                                                         redpack_event.invest_amount, datetime.datetime.fromtimestamp(stamp(endtime)).strftime('%Y年%m月%d日'))
            sentTemplate.apply_async(kwargs={"kwargs":json.dumps({
                                        "openid":weixin_user.openid,
                                        "template_id":BIND_SUCCESS_TEMPLATE_ID,
                                        "name1":"",
                                        "name2":weixin_user.user.wanglibaouserprofile.phone,
                                        "time":now_str+'\n',
                                        "remark":remark
                                            })},
                                        queue='celery02'
                                        )
            return
    sentTemplate.apply_async(kwargs={"kwargs":json.dumps({
                                "openid":weixin_user.openid,
                                "template_id":BIND_SUCCESS_TEMPLATE_ID,
                                "name1":"",
                                "name2":weixin_user.user.wanglibaouserprofile.phone,
                                "time":now_str,
                                    })},
                                queue='celery02'
                                )

@app.task
def detect_product_biding(product_id):
    product = P2PProduct.objects.get(pk=product_id)
    matches = re.search(u'日计息', product.pay_method)
    period = product.period
    period_desc = "%s个月"%product.period
    if matches and matches.group():
        period = period/30.0   # 天
        period_desc = '%s天'%product.period
    if product.activity:
        rate_desc = "%s%% + %s%%"%(product.expected_earning_rate, product.activity.rule.percent_text)
    else:
        rate_desc = "%s%%"%product.expected_earning_rate

    services = SubscribeService.objects.filter(channel='weixin', is_open=True, type=0).all()
    for service in services:
        if period == service.num_limit:
            sub_records = SubscribeRecord.objects.filter(service=service, status=True).all()
            for sub_record in sub_records:
                if sub_record.w_user and sub_record.w_user.subscribe==1 and sub_record.w_user.user:
                    publish_time = product.publish_time
                    utc_now = timezone.now()
                    if utc_now <= publish_time:
                        exec_time = publish_time + datetime.timedelta(minutes=1)
                        sendUserProductOnLine.apply_async(kwargs={
                                "openid": sub_record.w_user.openid,
                                "service_desc": service.describe,
                                "product_id": product.id,
                                "product_name": product.name,
                                "rate_desc": rate_desc,
                                "period_desc": period_desc,
                                "pay_method": product.pay_method,
                                },
                                                          eta= exec_time,
                                                          queue='celery02'
                                                          )
                    else:
                        sendUserProductOnLine.apply_async(kwargs={
                                "openid": sub_record.w_user.openid,
                                "service_desc": service.describe,
                                "product_id": product.id,
                                "product_name": product.name,
                                "rate_desc": rate_desc,
                                "period_desc": period_desc,
                                "pay_method": product.pay_method,
                            },
                                                          queue='celery02')

@app.task
def sendUserProductOnLine(openid, service_desc, product_id, product_name, rate_desc, period_desc, pay_method):
    w_user = WeixinUser.objects.filter(openid=openid).first()
    product = P2PProduct.objects.get(pk=product_id)
    if w_user and w_user.subscribe==1 and w_user.user and product.status == u'正在招标':
        url = settings.CALLBACK_HOST + '/weixin/view/detail/%s/'%product_id
        template = MessageTemplate(PRODUCT_ONLINE_TEMPLATE_ID,
            first=service_desc, keyword1=product_name, keyword2=rate_desc,
            keyword3=period_desc, keyword4=pay_method, url=url)
        SendTemplateMessage.sendTemplate(w_user, template)

@app.task
def sentTemplate(kwargs):
    json_kwargs = json.loads(kwargs)
    openid = json_kwargs.get('openid', "")
    template_id = json_kwargs.get('template_id', "")
    template_args = {}
    for k, v in json_kwargs.iteritems():
        if k == 'openid' or k == 'template_id':
            continue
        template_args[k]=v
    template = MessageTemplate(template_id, **template_args)
    w_user = WeixinUser.objects.filter(openid=openid).first()
    if w_user and template:
        SendTemplateMessage.sendTemplate(w_user, template)
