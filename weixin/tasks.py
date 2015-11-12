#!/usr/bin/env python
# encoding:utf-8
from celery.utils.log import get_task_logger

from django.forms import model_to_dict
from django.utils import timezone
from django.utils.timezone import get_current_timezone
from order.models import Order
from order.utils import OrderHelper

from wanglibao.celery import app
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_p2p.models import P2PProduct, P2PRecord, Earning, ProductAmortization, ProductType
from wanglibao_p2p.trade import P2POperator
from wanglibao_p2p.automatic import Automatic
from django.db.models import Sum, Q
from django.contrib.auth.models import User
from wanglibao_sms import messages
from wanglibao_sms.tasks import send_messages
from wanglibao_account import message as inside_message
from wanglibao.templatetags.formatters import period_unit
import time, datetime, re
from django.conf import settings

from weixin.models import SubscribeRecord, SubscribeService, WeixinUser
from weixin.constant import MessageTemplate, PRODUCT_ONLINE_TEMPLATE_ID
from weixin.views import SendTemplateMessage


@app.task
def detect_product_biding(product_id):
    try:
        product = P2PProduct.objects.get(pk=product_id)
        print product.__dict__
        matches = re.search(u'日计息', product.pay_method)
        period = product.period
        period_desc = "%s个月"%product.period
        if matches and matches.group():
            period = period/30.0   # 天
            period_desc = '%s天'%product.period
        rate_desc = "%s%%"%product.expected_earning_rate
        services = SubscribeService.objects.filter(channel='weixin', is_open=True, type=0).all()
        for service in services:
            if period == service.num_limit:
                sub_records = SubscribeRecord.objects.filter(service=service).all()
                for sub_record in sub_records:
                    sendUserProductOnLine.apply_async(kwargs={
                            "uid":sub_record.user.id,
                            "service_desc":service.describe,
                            "product_id":product.id,
                            "product_name":product.name,
                            "rate_desc":rate_desc,
                            "period_desc":period_desc,
                            "pay_method":product.pay_method,
                        })
    except:
        pass

@app.task
def sendUserProductOnLine(uid, service_desc, product_id, product_name, rate_desc, period_desc, pay_method):
    try:
        print '----------------------------------------1'
        user = User.objects.get(pk=uid)
        w_user = WeixinUser.objects.filter(user=user).first()
        if w_user:
            url = settings.CALLBACK_HOST + '/weixin/view/detail/%s/'%product_id
            template = MessageTemplate(PRODUCT_ONLINE_TEMPLATE_ID,
                first=service_desc, keyword1=product_name, keyword2=rate_desc,
                keyword3=period_desc, keyword4=pay_method, url=url)
            SendTemplateMessage.sendTemplate(w_user, template)
    except:
        print '----------------------------------------1'
        pass