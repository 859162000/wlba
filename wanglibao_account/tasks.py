#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import StringIO
import traceback
from django.contrib.auth.models import User
from common.tools import now, str_to_utc, parase_form_error
from wanglibao.celery import app
from marketing.utils import get_user_channel_record
from wanglibao_margin.forms import MarginRecordForm
from wanglibao_margin.utils import save_to_margin
from wanglibao_pay.forms import PayInfoForm
from wanglibao_p2p.forms import P2PRecordForm, UserAmortizationForm, P2PProductForm
from wanglibao_p2p.utils import save_to_p2p_equity, update_p2p_product_ordered_amount
from wanglibao_p2p.tasks import process_channel_product_push
from wanglibao_p2p.models import P2PProduct, UserAmortization
from .cooperation import CoopCallback
from .forms import UserForm, UserValidateForm

logger = logging.getLogger('wanglibao_tasks')


LOCAL_VAR = locals()


# @app.task
# def process_coop_common_callback(user_id, act, order_id=None):
#     channel = get_user_channel_record(user_id)
#     if channel:
#         CoopCallback(channel).process_all_callback(user_id, act, order_id)


def process_amortize(amortizations, product_id, sync_id, amo_act):
    logger.info("Enter process_amortize >>>>>>>>>>>> with product_id[%s]" % product_id)
    user_amo_list = list()
    for amo in amortizations:
        amo['sync_id'] = sync_id
        user_id = amo['user']
        term = amo['term']
        amo_instance = UserAmortization.objects.filter(user_id=user_id, product_id=product_id, term=term).first()
        if amo_instance:
            amo['settlement_time'] = str_to_utc(amo['settlement_time'])
            user_amo_form = UserAmortizationForm(amo, instance=amo_instance)
        else:
            amo['term_date'] = str_to_utc(amo['term_date'])
            user_amo_form = UserAmortizationForm(amo)

        if user_amo_form.is_valid():
            if amo_instance:
                user_amo = user_amo_form.save()
            else:
                user = User.objects.get(pk=user_id)
                amo['user'] = user
                p2p_product = P2PProduct.objects.get(pk=amo['product'])
                amo['product'] = p2p_product
                user_amo = UserAmortization()
                for k, v in amo.iteritems():
                    setattr(user_amo, k, v)
                user_amo.save()
            user_amo_list.append(user_amo)

            if (amo_act == 'plan' and amo['term'] == 1) or amo_act == 'amortize':
                response_data = save_to_margin(amo)
                logger.info("process_amortize save_to_margin amo[%s] result: [%s]" % (amo, response_data))

                response_data = save_to_p2p_equity(amo)
                logger.info("process_amortize save_to_p2p_equity amo[%s] result: [%s]" % (amo, response_data))
        else:
            logger.info("process_amortize data[%s] invalid error[%s]" % (amo, user_amo_form.errors))

    if user_amo_list:
        CoopCallback().process_amortize_callback(user_amo_list)


def process_recharge_callback(req_data):
    pay_info = req_data["pay_info"]
    margin_record = req_data["margin_record"]
    margin_record = json.loads(margin_record)
    margin_record["create_time"] = str_to_utc(margin_record["create_time"])
    margin_record_form = MarginRecordForm(margin_record)
    if margin_record_form.is_valid():
        pay_info = json.loads(pay_info)
        margin_record = margin_record_form.save()
        pay_info["margin_record"] = margin_record.id
        pay_info["create_time"] = str_to_utc(pay_info["create_time"])
        user_id = pay_info['user']
        pay_info_form = PayInfoForm(pay_info)
        if pay_info_form.is_valid():
            pay_info = pay_info_form.save()
            response_data = save_to_margin(req_data)
            if response_data['ret_code'] == 10000:
                channel = get_user_channel_record(user_id)
                if channel:
                    CoopCallback(channel).process_all_callback(user_id, 'recharge', pay_info.order_id)
        else:
            response_data = parase_form_error(pay_info_form)
    else:
        response_data = parase_form_error(margin_record_form)

    return response_data


def process_purchase_callback(req_data):
    margin_record = json.loads(req_data["margin_record"])
    margin_record["create_time"] = str_to_utc(margin_record["create_time"])
    user_id = margin_record['user_id']
    margin_record.pop('user_id', None)
    margin_record['user'] = user_id
    margin_record_form = MarginRecordForm(margin_record)
    if margin_record_form.is_valid():
        p2p_record = json.loads(req_data["p2p_record"])
        margin_record = margin_record_form.save()
        p2p_record["margin_record"] = margin_record.id
        p2p_record["create_time"] = str_to_utc(p2p_record["create_time"])
        p2p_record['user'] = p2p_record['user_id']
        p2p_record.pop('user_id', None)
        p2p_record_form = P2PRecordForm(p2p_record)
        if p2p_record_form.is_valid():
            p2p_record = p2p_record_form.save()

            # 更新标的已投金额
            product_id = p2p_record.product.id
            update_p2p_product_ordered_amount(product_id, p2p_record.product_balance_after)
            # 推送标的信息到第三方
            process_channel_product_push.apply_async(
                kwargs={'product_id': product_id}
            )

            save_margin_response_data = save_to_margin(req_data)
            save_equity_response_data = save_to_p2p_equity(req_data)
            if save_margin_response_data['ret_code'] == 10000:
                if save_equity_response_data['ret_code'] == 10000:
                    channel = get_user_channel_record(user_id)
                    if channel:
                        CoopCallback(channel).process_all_callback(user_id, 'purchase', p2p_record.order_id)
                    response_data = save_equity_response_data
                else:
                    response_data = save_equity_response_data
            else:
                response_data = save_margin_response_data
        else:
            response_data = parase_form_error(p2p_record_form)
    else:
        response_data = parase_form_error(margin_record_form)

    return response_data


def process_product_update_callback(req_data):
    product = json.loads(req_data["product"])
    product_id = product['id']
    product_instance = P2PProduct.objects.filter(pk=product_id).first()
    if product_instance:
        if 'product_balance_after' in product:
            product_balance_after = product['product_balance_after']
            product['ordered_amount'] = float(product_instance.total_amount) - float(product_balance_after)
            product.pop('product_balance_after', None)

        for k, v in product.iteritems():
            setattr(product_instance, k, v)
        product_instance.save()

        # 推送标的信息到第三方
        process_channel_product_push.apply_async(
            kwargs={'product_id': product_instance.id}
        )

        response_data = {
            'message': 'success',
            'ret_code': 10000,
        }
    else:
        response_data = {
            'message': u'无效产品id',
            'ret_code': 10001,
        }

    return response_data


def process_bind_card_callback(req_data):
    form = UserForm(req_data)
    if form.is_valid():
        user = form.cleaned_data['user_id']
        user.wanglibaouserprofile.is_bind_card = True
        user.wanglibaouserprofile.first_bind_card_time = now()
        user.wanglibaouserprofile.save()
        response_data = {
            'ret_code': 10000,
            'message': 'success',
        }
        # FixMe,异步回调给第三方
    else:
        response_data = parase_form_error(form)

    return response_data


def process_validate_callback(req_data):
    form = UserValidateForm(req_data)
    if form.is_valid():
        user = form.cleaned_data['user_id']
        name = form.cleaned_data['name']
        id_number = form.cleaned_data['id_number']
        id_valid_time = form.cleaned_data['id_valid_time']
        id_valid_time = str_to_utc(id_valid_time)
        user.wanglibaouserprofile.name = name
        user.wanglibaouserprofile.id_number = id_number
        user.wanglibaouserprofile.id_is_valid = True
        user.wanglibaouserprofile.id_valid_time = id_valid_time
        user.wanglibaouserprofile.save()
        response_data = {
            'ret_code': 10000,
            'message': 'success',
        }
        # FixMe,异步回调给第三方
    else:
        response_data = parase_form_error(form)

    return response_data


def process_withdraw_callback(req_data):
    return


def process_amortizations_push_callback(req_data):
    product_id = req_data['product_id']
    sync_id = req_data["sync_id"]
    try:
        p2p_product = P2PProduct.objects.get(pk=product_id)
    except P2PProduct.DoesNotExist:
        p2p_product = None

    if p2p_product:
        amortizations = json.loads(req_data['amortizations'])
        amo_act = req_data['amo_act']
        process_amortize(amortizations=amortizations, product_id=product_id, sync_id=sync_id, amo_act=amo_act)
        # .apply_async(
        # kwargs={'amortizations': amortizations, 'product_id': product_id, 'sync_id': sync_id})

        response_data = {
            'ret_code': 10000,
            'message': 'success',
        }
    else:
        response_data = {
            'ret_code': 10051,
            'message': u'无效产品id',
        }

    return response_data


def process_products_push_callback(req_data):
    products = json.loads(req_data['products'])
    sync_id = req_data["sync_id"]
    for product in products:
        product['sync_id'] = sync_id
        product['publish_time'] = str_to_utc(product['publish_time'])
        product['end_time'] = str_to_utc(product['end_time'])
        p_soldout_time = product.get('soldout_time', None)
        p_make_loans_time = product.get('make_loans_time', None)
        if p_soldout_time:
            product['soldout_time'] = str_to_utc(p_soldout_time)
        if p_make_loans_time:
            product['make_loans_time'] = str_to_utc(p_make_loans_time)

        if product['status'] == u'流标':
            product['flow_time'] = now()

        product_instance = P2PProduct.objects.filter(pk=product['id']).first()
        if product_instance:
            if ((product_instance.status == product['status'] and
                 product_instance.ordered_amount == product['ordered_amount']) or
                    sync_id < product_instance.sync_id):
                continue
            product_form = P2PProductForm(product, instance=product_instance)
        else:
            product_form = P2PProductForm(product)

        if product_form.is_valid():
            if product_instance:
                product_instance = product_form.save()
            else:
                product_instance = P2PProduct()
                for k, v in product.iteritems():
                    setattr(product_instance, k, v)
                product_instance.save()

            # 推送标的信息到第三方
            process_channel_product_push.apply_async(
                kwargs={'product_id': product_instance.id}
            )
        else:
            message = product_form.errors
            logger.info("process_products_push data[%s] invalid with form error: [%s]" % (product, message))

    logger.info("process_products_push done")
    response_data = {
        'ret_code': 10000,
        'message': 'success',
    }
    return response_data


@app.task
def coop_call_back(params):
        logger.info("Enter coop_call_back task===>>> with data[%s]" % params)

        # 判断动作有效性，并调度相关处理器
        act = params['act']
        processor_name = 'process_%s_callback' % act.lower()
        processor = LOCAL_VAR[processor_name]

        try:
            process_result = processor(params)
            logger.info("coop_call_back [%s] process result: [%s]" % (processor_name, process_result['message']))
        except:
            # 创建内存文件对象
            fp = StringIO.StringIO()
            traceback.print_exc(file=fp)
            message = fp.getvalue()
            logger.info("coop_call_back [%s] raise error: [%s]" % (processor_name, message))
