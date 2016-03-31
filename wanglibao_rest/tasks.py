#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from wanglibao.celery import app
from marketing.utils import get_user_channel_record
from wanglibao_account.tools import str_to_utc
from wanglibao_account.cooperation import CoopCallback
from wanglibao_p2p.models import P2PProduct, UserAmortization
from wanglibao_p2p.forms import UserAmortizationForm
from wanglibao_margin.utils import save_to_margin
from wanglibao_p2p.utils import save_to_p2p_equity

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
        amo_id = amo.get('id', None)
        if amo_id:
            amo_instance = UserAmortization.objects.filter(pk=amo_id).first()
            if amo_instance:
                amo['settlement_time'] = str_to_utc(amo['settlement_time'])
                user_amo_form = UserAmortizationForm(amo, instance=amo_instance)
            else:
                amo['product'] = p2p_product
                amo['term_date'] = str_to_utc(amo['term_date'])
                user_amo_form = UserAmortizationForm(amo)

            if user_amo_form.is_valid():
                if amo_instance:
                    user_amo = user_amo_form.save()
                else:
                    user_amo = UserAmortization()
                    for k, v in amo.iteritems():
                        setattr(user_amo, k, v)
                    user_amo.save()
                user_amo_list.append(user_amo)
                save_to_margin(amo)
                if user_amo.term == 1:
                    response_data = save_to_p2p_equity(amo)
            else:
                logger.info("process_amortizations_push data[%s] invalid" % user_amo_form.errors)

    if user_amo_list:
        CoopCallback().process_amortize_callback(user_amo_list)
