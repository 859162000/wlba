#!/usr/bin/env python
# encoding:utf-8

import json
import logging
import hashlib
import traceback
import StringIO
from rest_framework.views import APIView
from datetime import datetime as dt
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from marketing.models import Channels
from marketing.forms import ChannelForm
from wanglibao_account.models import Binding
from wanglibao_account.tools import str_to_utc
from wanglibao_account.utils import create_user
from wanglibao_account.forms import UserRegisterForm, UserForm, UserValidateForm
from wanglibao_account.cooperation import CoopRegister, CoopSessionProcessor, RenRenLiCallback
from wanglibao_p2p.models import P2PProduct, P2PRecord
from wanglibao_p2p.forms import P2PProductForm, P2PRecordForm
from wanglibao_p2p.tasks import process_channel_product_push
from wanglibao_p2p.utils import save_to_p2p_equity
from wanglibao_pay.forms import PayInfoForm
from wanglibao_margin.forms import MarginRecordForm
from wanglibao_margin.utils import save_to_margin
from wanglibao_oauth2.models import Client
from wanglibao_rest import utils as rest_utils
from wanglibao_rest.utils import has_binding_for_bid, get_coop_binding_for_phone
from .forms import CoopDataDispatchForm, AccessUserExistsForm, BiSouYiUserExistsForm
from .tasks import coop_common_callback, process_amortize
from .utils import utc_to_local_timestamp, generate_bisouyi_content, generate_bisouyi_sign


logger = logging.getLogger('wanglibao_rest')


class BidHasBindingForChannel(APIView):
    """
    根据bid（第三方用户ID）判断该用户是否已经绑定指定渠道
    """

    permission_classes = ()

    def get(self, request, channel_code, bid):
        has_binding = has_binding_for_bid(channel_code, bid)
        if has_binding:
            response_data = {
                'ret_code': 10001,
                'message': u'该bid已经绑定'
            }
        else:
            response_data = {
                'ret_code': 10000,
                'message': u'该bid未绑定'
            }

        return HttpResponse(json.dumps(response_data), content_type='application/json')


class AccessUserExistsApi(APIView):
    """第三方手机号注册及绑定状态检测接口"""

    permission_classes = ()

    def post(self, request):
        logger.info("enter AccessUserExistsApi with data [%s], [%s]" % (request.REQUEST, request.body))

        form = AccessUserExistsForm(request.session)
        channel_code = request.GET.get('promo_token')

        if form.is_valid():
            phone = form.cleaned_data['phone']
            user = User.objects.filter(wanglibaouserprofile__phone=phone).first()
            binding = get_coop_binding_for_phone(channel_code, phone)
            coop_sign_check = getattr(form, '%s_sign_check' % channel_code.lower(), None)
            sign_is_ok = coop_sign_check()
            coop_register_processor = getattr(rest_utils, 'process_%s_user_exists' % channel_code.lower(), None)
            response_data = coop_register_processor(user, binding, sign_is_ok)
        else:
            response_data = {
                'ret_code': 10020,
                'message': form.errors.values()[0][0],
            }

        if channel_code == 'bajinshe':
            response_data['code'] = response_data['ret_code']
            response_data.pop('ret_code')
            response_data['msg'] = response_data['message']
            response_data.pop('message')

        CoopSessionProcessor(request).all_processors_for_session(1)

        return HttpResponse(json.dumps(response_data), status=200, content_type='application/json')


class BiSouYiUserExistsApi(APIView):
    """第三方手机号注册及绑定状态检测接口"""

    permission_classes = ()

    def post(self, request):
        form = BiSouYiUserExistsForm(request.session)
        if form.is_valid():
            if form.check_sign():
                phone = form.get_phone()
                user = User.objects.filter(wanglibaouserprofile__phone=phone).first()
                _type = 0 if user else 1
                user_type = u'是' if user else u'否'
                content_data = {
                    'code': 10000,
                    'message': 'success',
                    'status': 1,
                    'yaccount': user_type,
                    'mobile': phone,
                    'type': _type,
                }
            else:
                content_data = {
                    'code': 10010,
                    'message': u'无效签名',
                }
        else:
            content_data = {
                'code': 10020,
                'message': form.errors.values()[0][0],
            }

        content_data['pcode'] = settings.BISOUYI_PCODE
        if content_data['code'] != 10000:
            content_data['status'] = 0

        content = generate_bisouyi_content(content_data)
        client_id = settings.BISOUYI_CLIENT_ID
        sign = generate_bisouyi_sign(content)
        response_data = {
            'cid': client_id,
            'sign': sign,
            'conten': content,
        }

        http_response = HttpResponse(json.dumps(response_data), status=200, content_type='application/json')
        http_response['cid'] = client_id
        http_response['sign'] = sign

        CoopSessionProcessor(request).all_processors_for_session(1)
        return http_response


class CoopDataDispatchApi(APIView):
    """
    渠道中心平台数据调度接口
    """

    permission_classes = ()

    def parase_form_error(self, form_errors):
        response_data = {
            'ret_code': 50003,
            'message': form_errors.values()[0][0]
        }
        return response_data

    def process_new_channel(self, req_data):
        logger.info("channel data dispatch enter save_to_channel")
        form = ChannelForm(req_data)
        if form.is_valid():
            channel_code = form.cleaned_data['channel_code']
            channel_name = form.cleaned_data['channel_name']
            try:
                channel = Channels(code=channel_code, name=channel_name)
                channel.save()
                response_data = {
                    'ret_code': 10000,
                    'message': 'success',
                }
            except Exception, e:
                response_data = {
                    'ret_code': 50001,
                    'message': 'api error',
                }
                logger.info(e)
        else:
            response_data = self.parase_form_error(form.errors)

        return response_data

    def process_register(self, req_data):
        logger.info("channel data dispatch enter process_register")
        form = UserRegisterForm(req_data)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            phone = form.cleaned_data['phone']
            btype = form.cleaned_data['btype']
            bid = req_data.get('bid')
            client_id = req_data.get('client_id')
            order_id = req_data.get('order_id')
            access_token = req_data.get('access_token')
            account = req_data.get('account')
            user = create_user(user_id, phone)
            if user:
                try:
                    CoopRegister(btype, bid, client_id,
                                 order_id, access_token, account).all_processors_for_user_register(user)
                except Exception, e:
                    response_data = {
                        'ret_code': 10025,
                        'message': 'coop register error',
                    }
                    logger.info("process_register raise error: %s" % e)
                else:
                    response_data = {
                        'ret_code': 10000,
                        'message': 'success',
                    }
            else:
                response_data = {
                    'ret_code': 10023,
                    'message': u'用户创建失败',
                }
        else:
            response_data = self.parase_form_error(form.errors)

        return response_data

    def process_recharge(self, req_data):
        pay_info = req_data.get("pay_info", '')
        margin_record = req_data.get("margin_record", '')

        if pay_info and margin_record:
            margin_record = json.loads(margin_record)
            margin_record["create_time"] = str_to_utc(margin_record["create_time"])
            margin_record_form = MarginRecordForm(margin_record)
            if margin_record_form.is_valid():
                pay_info = json.loads(pay_info)
                margin_record = margin_record_form.save()
                pay_info["margin_record"] = margin_record.id
                pay_info["create_time"] = str_to_utc(pay_info["create_time"])
                pay_info_form = PayInfoForm(pay_info)
                if pay_info_form.is_valid():
                    pay_info = pay_info_form.save()
                    response_data = save_to_margin(req_data)
                    coop_common_callback.apply_async(
                        kwargs={'user_id': pay_info.user_id, 'act': 'recharge', 'order_id': pay_info.order_id})
                else:
                    response_data = self.parase_form_error(pay_info_form.errors)
            else:
                response_data = self.parase_form_error(margin_record_form.errors)
        else:
            response_data = {
                'ret_code': 10111,
                'message': u'缺少业务参数',
            }

        return response_data

    def process_purchase(self, req_data):
        p2p_record = req_data.get("p2p_record")
        margin_record = req_data.get("margin_record")
        if p2p_record and margin_record:
            margin_record = json.loads(margin_record) if margin_record else None
            margin_record["create_time"] = str_to_utc(margin_record["create_time"])
            margin_record_form = MarginRecordForm(margin_record)
            if margin_record_form.is_valid():
                p2p_record = json.loads(p2p_record) if p2p_record else None
                margin_record = margin_record_form.save()
                p2p_record["margin_record"] = margin_record.id
                p2p_record["create_time"] = str_to_utc(p2p_record["create_time"])
                p2p_record['user'] = p2p_record.get('user_id')
                p2p_record_form = P2PRecordForm(p2p_record)
                if p2p_record_form.is_valid():
                    p2p_record = p2p_record_form.save()
                    save_margin_response_data = save_to_margin(req_data)
                    save_equity_response_data = save_to_p2p_equity(req_data)
                    if save_margin_response_data['ret_code'] != 10000:
                        response_data = save_margin_response_data
                    else:
                        response_data = save_equity_response_data

                    coop_common_callback.apply_async(
                        kwargs={'user_id': p2p_record.user_id, 'act': 'purchase', 'order_id': p2p_record.order_id})
                else:
                    response_data = self.parase_form_error(p2p_record_form.errors)
            else:
                response_data = self.parase_form_error(margin_record_form.errors)
        else:
            response_data = {
                'ret_code': 10111,
                'message': u'缺少业务参数',
            }
        return response_data

    def process_bind_card(self, req_data):
        form = UserForm(req_data)
        if form.is_valid():
            user = form.cleaned_data['user_id']
            user.wanglibaouserprofile.is_bind_card = True
            user.wanglibaouserprofile.first_bind_card_time = timezone.now()
            user.wanglibaouserprofile.save()
            response_data = {
                'ret_code': 10000,
                'message': 'success',
            }
            # FixMe,异步回调给第三方
        else:
            response_data = self.parase_form_error(form.errors)

        return response_data

    def process_validate(self, req_data):
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
            response_data = self.parase_form_error(form.errors)

        return response_data

    def process_withdraw(self, req_data):
        return

    def process_amortizations_push(self, req_data):
        product_id = req_data.get('product_id')
        amortizations = req_data.get('amortizations')
        if product_id and amortizations:
            try:
                p2p_product = P2PProduct.objects.get(pk=product_id)
            except P2PProduct.DoesNotExist:
                p2p_product = None

            if p2p_product:
                amortizations = json.loads(amortizations)
                process_amortize.apply_async(
                    kwargs={'amortizations': amortizations, 'product_id': product_id})

                response_data = {
                    'ret_code': 10000,
                    'message': 'success',
                }
            else:
                response_data = {
                    'ret_code': 10051,
                    'message': u'无效产品id',
                }
        else:
            response_data = {
                'ret_code': 50002,
                'message': u'非法请求',
            }
        return response_data

    def process_products_push(self, req_data):
        products = req_data.get('products')
        if products:
            products = json.loads(products)
            for product in products:
                product['publish_time'] = str_to_utc(product['publish_time'])
                product['end_time'] = str_to_utc(product['end_time'])
                p_soldout_time = product.get('soldout_time', None)
                p_make_loans_time = product.get('make_loans_time', None)
                if p_soldout_time:
                    product['soldout_time'] = str_to_utc(p_soldout_time)
                if p_make_loans_time:
                    product['make_loans_time'] = str_to_utc(p_make_loans_time)

                product_instance = P2PProduct.objects.filter(pk=product['id']).first()
                if product_instance:
                    if product_instance.status == product['status']:
                        continue
                    product_form = P2PProductForm(product, instance=product_instance)
                else:
                    product_form = P2PProductForm(product)

                if product_form.is_valid():
                    if product_instance:
                            product_form.save()
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
                    logger.info("process_products_push data[%s] invalid with form error: %s" % (product, message))

        logger.info("process_products_push done")
        response_data = {
            'ret_code': 10000,
            'message': 'success',
        }
        return response_data

    def post(self, request):
        req_data = request.POST
        logger.info("channel data dispatch processing with %s" % req_data)
        form = CoopDataDispatchForm(req_data)
        processer = None
        if form.is_valid():
            channel = form.cleaned_data['channel']
            _time = form.cleaned_data['time']
            sign = form.cleaned_data['sign']
            act = form.cleaned_data['act']
            # 判断数据签名有效性
            key = getattr(settings, '%s_SYNC_KEY' % channel.upper(), None)
            if key:
                is_right_sign = form.check_sign(channel, _time, key, sign)
                if is_right_sign:
                    # 判断动作有效性，并调度相关处理器
                    processer = getattr(self, 'process_%s' % act, None)
                    if processer:
                        try:
                            response_data = processer(req_data)
                        except:
                            # 创建内存文件对象
                            fp = StringIO.StringIO()
                            traceback.print_exc(file=fp)
                            message = fp.getvalue()
                            logger.info("CoopDataDispatchApi %s raise error: %s" % (processer.__name__, message))
                            response_data = {
                                'ret_code': 50001,
                                'message': 'api error',
                            }
                    else:
                        response_data = {
                            'ret_code': 10004,
                            'message': u'无效动作',
                        }
                else:
                    response_data = {
                        'ret_code': 10003,
                        'message': u'无效签名',
                    }
            else:
                response_data = {
                    'ret_code': 10001,
                    'message': u'渠道签名key不存在',
                }
        else:
            response_data = self.parase_form_error(form.errors)

        if processer:
            logger.info('channel data dispatch %s result:%s' % (processer.__name__, response_data['message']))
        else:
            logger.info('channel data dispatch process result:%s' % response_data['message'])

        return HttpResponse(json.dumps(response_data), status=200, content_type='application/json')


class RenRenLiQueryApi(APIView):
    permission_classes = ()

    def check_sign(self, client_id, order_id, bid, key, sign):
        local_sign = hashlib.md5(client_id + str(order_id) + str(bid) + key).hexdigest()

        if local_sign == sign:
            return True
        else:
            return False

    def get_amotize_data(self, data, p2p_record):
        if p2p_record.product.soldout_time:
            soldout_time = p2p_record.product.soldout_time or 0
            amotized_amount = p2p_record.amotized_amount or 0
            invest_end_time = p2p_record.invest_end_time or 0
            back_last_date = p2p_record.back_last_date or 0
            data['Invest_full_scale_date'] = utc_to_local_timestamp(soldout_time) if soldout_time else soldout_time
            data['Back_money'] = float(amotized_amount) if amotized_amount else amotized_amount
            data['Invest_end_date'] = utc_to_local_timestamp(invest_end_time) if invest_end_time else invest_end_time
            data['Back_last_date'] = utc_to_local_timestamp(back_last_date) if back_last_date else back_last_date

        return data

    def post(self, request):
        req_data = request.POST
        sign = req_data.get('Sign', None)
        client_id = req_data.get('Cust_id', None)
        order_id = req_data.get('Order_no', '')
        bid = req_data.get('Cust_key', '')
        start_time = req_data.get('Start_date', None)
        end_time = req_data.get('End_date', None)

        if sign:
            if client_id:
                client = Client.objects.filter(client_id=client_id).select_related('channel').first()
                if client:
                    is_right_sign = self.check_sign(client_id, order_id, bid, client.client_secret, sign)
                    if is_right_sign:
                        data_list = list()
                        renrenli_callback = RenRenLiCallback(client.channel)
                        if order_id:
                            p2p_record = P2PRecord.objects.filter(order_id=order_id).select_related().first()
                            if p2p_record:
                                data = renrenli_callback.get_purchase_data(p2p_record)
                                if data:
                                    data = self.get_amotize_data(data, p2p_record)
                                    data_list.append(data)

                                response_data = {
                                    'Code': 101,
                                    'Data': json.dumps(data_list),
                                }
                            else:
                                response_data = {
                                    'Code': 10014,
                                    'Data': u'无效订单号',
                                }
                        elif bid:
                            binding = Binding.objects.filter(btype=client.channel.code, bid=bid).first()
                            if binding:
                                if start_time:
                                    start_time = dt.fromtimestamp(float(start_time[:10]))
                                    if end_time:
                                        end_time = dt.fromtimestamp(float(end_time[:10]))
                                    else:
                                        end_time = dt.now()
                                    p2p_records = P2PRecord.objects.filter(user_id=binding.user.id,
                                                                           create_time__gte=start_time,
                                                                           create_time__lte=end_time).select_related()
                                    if p2p_records:
                                        for p2p_record in p2p_records:
                                            data = renrenli_callback.get_purchase_data(p2p_record)
                                            if data:
                                                data = self.get_amotize_data(data, p2p_record)
                                                data_list.append(data)

                                    response_data = {
                                        'Code': 101,
                                        'Data': json.dumps(data_list),
                                    }
                                else:
                                    response_data = {
                                        'Code': 10016,
                                        'Data': u'起始时间不存在',
                                    }
                            else:
                                response_data = {
                                    'Code': 10015,
                                    'Data': u'无效用户绑定id',
                                }
                        else:
                            if start_time:
                                start_time = dt.fromtimestamp(float(start_time[:10]))
                                if end_time:
                                    end_time = dt.fromtimestamp(float(end_time[:10]))
                                else:
                                    end_time = dt.now()
                                p2p_records = P2PRecord.objects.filter(user__binding__channel__code='renrenli',
                                                                       create_time__gte=start_time,
                                                                       create_time__lte=end_time).select_related()
                                if p2p_records:
                                    for p2p_record in p2p_records:
                                        data = renrenli_callback.get_purchase_data(p2p_record)
                                        if data:
                                            data = self.get_amotize_data(data, p2p_record)
                                            data_list.append(data)

                                response_data = {
                                    'Code': 101,
                                    'Data': json.dumps(data_list),
                                }
                            else:
                                response_data = {
                                    'Code': 10016,
                                    'Data': u'起始时间不存在',
                                }
                    else:
                        response_data = {
                            'Code': 10013,
                            'Data': u'无效签名',
                        }
                else:
                    response_data = {
                        'Code': 10012,
                        'Data': u'无效客户端id不存在',
                    }
            else:
                response_data = {
                    'Code': 10011,
                    'Data': u'客户端id不存在',
                }
        else:
            response_data = {
                'Code': 10010,
                'Data': u'签名不存在',
            }

        return HttpResponse(json.dumps(response_data), status=200, content_type='application/json')
