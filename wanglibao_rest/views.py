#!/usr/bin/env python
# encoding:utf-8

import json
import logging
import hashlib
import traceback
import StringIO
from rest_framework.views import APIView
from datetime import datetime as dt
from django.http import HttpResponse
from django.conf import settings
from common.tools import utc_to_local_timestamp
from marketing.models import Channels
from marketing.forms import ChannelForm
from wanglibao_account.models import Binding
from wanglibao_account.utils import create_user, has_binding_for_bid
from wanglibao_account.forms import UserRegisterForm
from wanglibao_account.cooperation import CoopRegister, RenRenLiCallback
from wanglibao_p2p.models import P2PRecord
from wanglibao_oauth2.models import Client
from .forms import CoopDataDispatchForm


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
            # amotized_amount = p2p_record.amotized_amount or 0
            invest_end_time = p2p_record.invest_end_time or 0
            # back_last_date = p2p_record.back_last_date or 0
            data['Invest_full_scale_date'] = utc_to_local_timestamp(soldout_time) if soldout_time else soldout_time
            data['Back_money'] = 0
            data['Invest_end_date'] = utc_to_local_timestamp(invest_end_time) if invest_end_time else invest_end_time
            data['Back_last_date'] = 0

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
                            binding = Binding.objects.filter(channel=client.channel, bid=bid).first()
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
