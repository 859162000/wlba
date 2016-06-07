#!/usr/bin/env python
# encoding:utf-8

from wanglibao.celery import app
from wanglibao_p2p.models import P2PProduct
import re
import json
from django.conf import settings
from django.utils import timezone
import datetime

from wechatpy import WeChatClient
from weixin.models import SubscribeRecord, SubscribeService, WeixinUser, WeixinAccounts
from weixin.constant import MessageTemplate, PRODUCT_ONLINE_TEMPLATE_ID
from weixin.util import sendTemplate, getMiscValue
from weixin.constant import BIND_SUCCESS_TEMPLATE_ID



@app.task
def bind_ok(openid, is_first_bind, new_registed=False):
    weixin_user = WeixinUser.objects.get(openid=openid)
    now_str = datetime.datetime.now().strftime('%Y年%m月%d日')
    user = weixin_user.user
    if is_first_bind:
        from wanglibao_activity.tasks import check_activity_task
        check_activity_task.apply_async(kwargs={
                "user_id": user.id,
                "trigger_node": 'first_bind_weixin',
                "device_type": 'weixin',
                "is_first_bind": is_first_bind,
            }, queue='celery02')
        # check_activity(user, 'first_bind_weixin', "weixin", is_first_bind=is_first_bind)
    else:
        sentTemplate.apply_async(kwargs={
            "kwargs": json.dumps({
                "openid": weixin_user.openid,
                "template_id": BIND_SUCCESS_TEMPLATE_ID,
                "name1": "",
                "name2": user.wanglibaouserprofile.phone,
                "time": now_str,
            })
        }, queue='celery02')
    from wanglibao_invite.tasks import processShareInviteDailyReward
    processShareInviteDailyReward.apply_async(
            kwargs={'openid': openid, 'user_id': user.id, "new_registed": new_registed})


@app.task
def detect_product_biding(product_id):

    def _sendProductToUser(openid, service_desc, product_id, product_name, rate_desc, period_desc, pay_method):
            sendUserProductOnLine.apply_async(kwargs={
                    "openid": openid,
                    "service_desc": service_desc,
                    "product_id": product_id,
                    "product_name": product_name,
                    "rate_desc": rate_desc,
                    "period_desc": period_desc,
                    "pay_method": pay_method,
                }, queue='celery02')

    product = P2PProduct.objects.get(pk=product_id)
    utc_now = timezone.now()
    if product.status == u'正在招标' and utc_now >= product.publish_time:
        matches = re.search(u'日计息', product.pay_method)
        period = product.period
        period_desc = "%s个月"%product.period
        is_day_product = False
        if matches and matches.group():
            is_day_product = True
            period_desc = '%s天'%product.period
        if product.activity:
            rate_desc = "%s%% + %s%%"%(product.expected_earning_rate, product.activity.rule.percent_text)
        else:
            rate_desc = "%s%%"%product.expected_earning_rate
        if is_day_product:
            day_service = SubscribeService.objects.filter(channel='weixin', is_open=True, type=1).first()
            if day_service:
                sub_records = SubscribeRecord.objects.filter(service=day_service, status=True).all()
                for sub_record in sub_records:
                    if sub_record.w_user and sub_record.w_user.subscribe==1 and sub_record.w_user.user:
                        _sendProductToUser(sub_record.w_user.openid, day_service.describe, product.id, product.name, rate_desc, period_desc, product.pay_method)

        else:
            services = SubscribeService.objects.filter(channel='weixin', is_open=True, type=0).all()
            for service in services:
                if period == service.num_limit:
                    sub_records = SubscribeRecord.objects.filter(service=service, status=True).all()
                    for sub_record in sub_records:
                        if sub_record.w_user and sub_record.w_user.subscribe==1 and sub_record.w_user.user:
                            _sendProductToUser(sub_record.w_user.openid, service.describe, product.id, product.name, rate_desc, period_desc, product.pay_method)

        finance_service = SubscribeService.objects.filter(channel='weixin', finance_type=product.types.fiance_type, is_open=True, type=2).first()
        if finance_service:
            sub_records = SubscribeRecord.objects.filter(service=finance_service, status=True).all()
            for sub_record in sub_records:
                if sub_record.w_user and sub_record.w_user.subscribe==1 and sub_record.w_user.user:
                    _sendProductToUser(sub_record.w_user.openid, finance_service.describe, product.id, product.name, rate_desc, period_desc, product.pay_method)


@app.task
def sendUserProductOnLine(openid, service_desc, product_id, product_name, rate_desc, period_desc, pay_method):
    w_user = WeixinUser.objects.filter(openid=openid).first()
    product = P2PProduct.objects.get(pk=product_id)
    if w_user and w_user.subscribe==1 and w_user.user and product.status == u'正在招标':
        url = settings.CALLBACK_HOST + '/weixin/sub_detail/detail/%s/'%product_id
        template = MessageTemplate(PRODUCT_ONLINE_TEMPLATE_ID,
            first=service_desc, keyword1=product_name, keyword2=rate_desc,
            keyword3=period_desc, keyword4=pay_method, url=url)
        sendTemplate(w_user, template)


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
    if w_user and template and w_user.subscribe:
        sendTemplate(w_user, template)

@app.task
def sentCustomerMsg(txt, openid):
    fwh_info = getMiscValue("weixin_qrcode_info")
    original_id = fwh_info.get("fwh")
    if original_id:
        weixin_account = WeixinAccounts.getByOriginalId(original_id)
        client = WeChatClient(weixin_account.app_id, weixin_account.app_secret)
        client.message._send_custom_message({
                                    "touser":openid,
                                    "msgtype":"text",
                                    "text":
                                    {
                                        "content": txt
                                    }
                                }, account="007@wanglibao400")
