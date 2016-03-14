#!/usr/bin/env python
# encoding:utf-8

import json
import requests
from celery.utils.log import get_task_logger

from django.db.models import Q
from django.utils import timezone
from wanglibao.celery import app
from wanglibao_p2p.models import P2PProduct
from wanglibao_account.utils import get_bajinshe_access_token
from django.conf import settings

logger = get_task_logger(__name__)


@app.task
def bajinshe_product_push():
    push_url = settings.BAJINSHE_PRODUCT_PUSH_URL
    coop_id = settings.BAJINSHE_COOP_ID
    coop_key = settings.BAJINSHE_COOP_KEY
    order_id = '%s_0000' % timezone.now().strftime("%Y%m%d%H%M%S")
    access_token = get_bajinshe_access_token(coop_id, coop_key, order_id)
    if access_token:
        product_list = P2PProduct.objects.filter(Q(status=u'已完成') & Q(make_loans_time__isnull=False) &
                                                 Q(make_loans_time__gte=timezone.now()-timezone.timedelta(days=1)))
        if product_list.exists():
            product_data_list = []
            for product in product_list:
                product_total_amount = product.total_amount
                product_status = product.status
                pay_method = product.pay_method
                if pay_method == u'等额本息':
                    pay_method_code = 3
                elif pay_method == u'按月付息':
                    pay_method_code = 1
                elif pay_method == u'日计息一次性还本付息':
                    pay_method_code = 2
                else:
                    pay_method_code = 11

                if product_status == u'正在招标':
                    product_status_code = 1
                elif product_status == u'已完成':
                    product_status_code = 2
                elif product_status in (u'录标', u'录标完成', u'待审核'):
                    product_status_code = 3
                elif product_status == u'还款中':
                    product_status_code = 5
                else:
                    product_status_code = 0

                if pay_method in [u'等额本息', u'按月付息', u'到期还本付息']:
                    periodType = 1
                else:
                    periodType = 2

                product_data = {
                    'pid': product.id,
                    'productType': 2,
                    'productName': product.name,
                    'apr': product.expected_earning_rate,
                    'amount': product_total_amount,
                    'pmType': pay_method_code,
                    'minIa': 100,
                    'progress': float('%.1f' % (float(product.ordered_amount) / product_total_amount * 100)),
                    'status': product_status_code,
                    'period': product.period,
                    'periodType': periodType,
                }

                product_data_list.append(product_data)
            else:
                data = {
                    'access_token': access_token,
                    'platform': coop_id,
                    'order_id': order_id,
                    'prod': product_data_list,
                }

            headers = {
               'Content-Type': 'application/json',
            }
            res = requests.post(url=push_url, data=json.dumps(data), headers=headers)
            res_status_code = res.status_code
            logger.info("bajinshe push product url %s" % res.url)
            if res_status_code == 200:
                res_data = res.json()
                if res_data['code'] != '10000':
                    logger.info("bajinshe push product return %s" % res_data)
                else:
                    logger.info("bajinshe push product,count[%s],suceess" % len(product_data_list))
            else:
                logger.info("bajinshe push product connect failed with status code [%s]" % res_status_code)
                logger.info(res.text)
