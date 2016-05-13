#!/usr/bin/env python
# encoding:utf-8

import json
import logging
from django.db.models import Q
from django.utils import timezone
from django.conf import settings

from common.tools import now
from common.tasks import common_callback
from wanglibao.celery import app
from wanglibao_account.utils import get_bajinshe_access_token, bisouyi_callback
from .models import P2PProduct
from .utils import (generate_bajinshe_product_data, generate_bisouyi_product_data)

logger = logging.getLogger('wanglibao_tasks')

_LOCALS = locals()


@app.task
def bajinshe_product_push(product=None, product_list=None):
    push_url = settings.BAJINSHE_PRODUCT_PUSH_URL
    coop_id = settings.BAJINSHE_COOP_ID
    order_id = '%s_0000' % now().strftime("%Y%m%d%H%M%S")
    access_token = get_bajinshe_access_token(order_id)
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

            common_callback.apply_async(
                kwargs={'channel': 'bajinshe', 'url': push_url,
                        'params': json.dumps(data), 'headers': headers})


@app.task
def bisouyi_product_push(product=None, product_list=None):
    product_data_list = list()
    product_data_status_list = list()
    if not product:
        if product_list and product_list.exists():
            for product in product_list:
                product_data = generate_bisouyi_product_data(product, 'info')
                product_status_data = generate_bisouyi_product_data(product, 'status')
                product_data_list.append(product_data)
                product_data_status_list.append(product_status_data)
    else:
        product_data = generate_bisouyi_product_data(product, 'info')
        product_status_data = generate_bisouyi_product_data(product, 'status')
        product_data_list.append(product_data)
        product_data_status_list.append(product_status_data)

    bisouyi_callback(settings.BISOUYI_PRODUCT_PUSH_URL, product_data_list, 'bisouyi', async_callback=False)

    bisouyi_callback(settings.BISOUYI_PRODUCT_STATUS_PUSH_URL, product_data_status_list, 'bisouyi')


@app.task
def process_channel_product_push(product_id=None, product=None):
    push_product_channels = settings.PUSH_PRODUCT_CHANNELS
    if push_product_channels:
        product_list = None
        if not product_id and not product:
            product_list = P2PProduct.objects.filter(~Q(status__in=(u'已完成', u'流标')) |
                                                     (Q(status=u'已完成') &
                                                      Q(make_loans_time__isnull=False) &
                                                      Q(make_loans_time__gte=now()-timezone.timedelta(days=1))))
        elif not product:
            product = P2PProduct.objects.filter(pk=product_id).first()

        for channel in push_product_channels:
            processor_name = '%s_product_push' % channel.lower()
            try:
                processor = _LOCALS[processor_name]
                processor(product=product, product_list=product_list)
            except Exception, e:
                logger.warning("process_channel_product_push dispatch %s raise error: %s" % (processor_name, e))
