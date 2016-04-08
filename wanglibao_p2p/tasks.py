#!/usr/bin/env python
# encoding:utf-8

import json
import requests
from celery.utils.log import get_task_logger

from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from wanglibao.celery import app
from wanglibao_rest.utils import generate_bisouyi_sign, generate_bisouyi_content
from wanglibao_account.utils import get_bajinshe_access_token
from wanglibao_account.tasks import common_callback_for_post
from .models import P2PProduct
from .utils import (generate_bajinshe_product_data, generate_bisouyi_product_data)

logger = get_task_logger(__name__)

_LOCALS = locals()


@app.task
def bajinshe_product_push(product=None, product_list=None):
    push_url = settings.BAJINSHE_PRODUCT_PUSH_URL
    coop_id = settings.BAJINSHE_COOP_ID
    coop_key = settings.BAJINSHE_COOP_KEY
    order_id = '%s_0000' % timezone.now().strftime("%Y%m%d%H%M%S")
    access_token = get_bajinshe_access_token(coop_id, coop_key, order_id)
    if access_token:
        product_data_list = list()
        if not product:
            if product_list and product_list.exists():
                for product in product_list:
                    product_data = generate_bajinshe_product_data(product)
                    product_data_list.append(product_data)
        else:
            product_data = generate_bajinshe_product_data(product)
            product_data_list.append(product_data)

        if product_data_list:
            data = {
                'access_token': access_token,
                'platform': coop_id,
                'order_id': order_id,
                'prod': product_data_list,
            }

            headers = {
               'Content-Type': 'application/json',
            }
            common_callback_for_post(url=push_url, params=json.dumps(data), channel='bajinshe', headers=headers)


@app.task
def bisouyi_product_push(product=None, product_list=None):
    product_data_list = list()
    if not product:
        if product_list and product_list.exists():
            for product in product_list:
                product_data = generate_bisouyi_product_data(product, 'info')
                product_status_data = generate_bisouyi_product_data(product, 'status')
                product_data_list.append((product_data, product_status_data))
    else:
        product_data = generate_bisouyi_product_data(product, 'info')
        product_status_data = generate_bisouyi_product_data(product, 'status')
        product_data_list.append((product_data, product_status_data))

    for product_data, product_status_data in product_data_list:
        headers = {
            'Content-Type': 'application/json',
            'cid': settings.BISOUYI_CLIENT_ID,
        }
        product_data_content = generate_bisouyi_content(product_data)
        product_data_sign = generate_bisouyi_sign(product_data_content)
        headers['sign'] = product_data_sign
        data = {'content': product_data_content}
        common_callback_for_post(url=settings.BISOUYI_PRODUCT_PUSH_URL, params=json.dumps(data),
                                 channel='bisouyi', headers=headers)

        product_status_data_content = generate_bisouyi_content(product_status_data)
        product_status_data_sign = generate_bisouyi_sign(product_status_data_content)
        headers['sign'] = product_status_data_sign
        data = {'content': product_status_data_content}
        common_callback_for_post(url=settings.BISOUYI_PRODUCT_PUSH_URL, params=json.dumps(data),
                                 channel='bisouyi', headers=headers)


@app.task
def process_channel_product_push(product=None):
    product_list=None
    if not product:
        product_list = P2PProduct.objects.filter(~Q(status=u'已完成') |
                                                 (Q(status=u'已完成') &
                                                  Q(make_loans_time__isnull=False) &
                                                  Q(make_loans_time__gte=timezone.now()-timezone.timedelta(days=1))))
    for k, v in _LOCALS.iteritems():
        if k.lower().find('_product_push') != -1:
            try:
                v(product=product, product_list=product_list)
            except Exception, e:
                logger.warning("process_channel_product_push dispatch %s raise error: %s" % (k, e))
