#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime as dt
import logging
from wanglibao.celery import app
from marketing.utils import get_user_channel_record
from wanglibao_account.cooperation import CoopCallback
from wanglibao_p2p.models import P2PProduct
from wanglibao_p2p.forms import UserAmortizationForm

logger = logging.getLogger(__name__)


@app.task
def coop_common_callback(user_id, act, order_id=None):
    channel = get_user_channel_record(user_id)
    if channel:
        CoopCallback(channel).process_all_callback(user_id, act, order_id)


@app.task
def process_amortize(amortizations, product_id):
    user_amo_list = list()
    p2p_product = P2PProduct.objects.get(pk=product_id)
    for amo in amortizations:
        amo['product'] = p2p_product
        amo['settlement_time'] = dt.strptime(amo['settlement_time'], '%Y-%m-%d %H:%M:%S')
        user_amo_form = UserAmortizationForm(amo)
        if user_amo_form.is_valid():
            user_amo = user_amo_form.save()
            user_amo_list.append(user_amo)
        else:
            logger.info("process_amortizations_push data[%s] invalid" % user_amo_form.errors)

    if user_amo_list:
        CoopCallback().process_amortize_callback(user_amo_list)
