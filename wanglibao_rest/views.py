#!/usr/bin/env python
# encoding:utf-8

import json
import logging
import hashlib
import traceback
import StringIO

import time
from decimal import Decimal
import datetime
import re
from rest_framework import renderers
from rest_framework.views import APIView
from datetime import datetime as dt
from django.http import HttpResponse
from django.conf import settings
from common.tools import utc_to_local_timestamp, timestamp_to_utc, utype_is_mobile
from common.utils import get_product_period_type
from marketing.models import Channels
from marketing.forms import ChannelForm
from marketing.utils import get_channel_record
from wanglibao_account.models import Binding
from wanglibao_account.utils import create_user, has_binding_for_bid
from wanglibao_account.forms import UserRegisterForm
from wanglibao_account.cooperation import CoopRegister, RenRenLiCallback
from wanglibao_p2p.models import P2PRecord, P2PEquity
from wanglibao_oauth2.models import Client
from .forms import CoopDataDispatchForm
from .utils import check_tan66_sign


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


class TanLiuLiuInvestmentQueryAPi(APIView):
    """
    弹66用户投资查询接口
    """
    permission_classes = ()

    def post(self, request):
        channel_code = self.request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, None)
        starttime = self.request.POST.get('starttime', None)
        endtime = self.request.POST.get('endtime', None)
        channel_account = self.request.POST.get('username', None)
        channel_user_uid = self.request.POST.get('usernamep', None)
        if channel_code and starttime and endtime:
            channel = get_channel_record(channel_code)
            if channel:
                if check_tan66_sign(request):
                    p2p_list = []
                    ret = dict()
                    bind = Binding.objects.filter(channel=channel, bid=channel_user_uid).first()
                    if bind:
                        starttime = timestamp_to_utc(starttime)
                        endtime = timestamp_to_utc(endtime)
                        p2p_records = P2PRecord.objects.filter(user=bind.user, created_at__gte=starttime,
                                                               created_at__lte=endtime)
                        for p2p_record in p2p_records:
                            p2p_product = p2p_record.product
                            rate = p2p_product.get_p2p_rate
                            p_type = get_product_period_type(p2p_product.pay_method)

                            p2p_dict = dict()
                            p2p_dict['oid'] = p2p_record.order_id
                            p2p_dict['bid'] = p2p_product.id
                            p2p_dict['title'] = p2p_product.name

                            if utype_is_mobile(request):
                                p2p_dict['url'] = settings.WLB_URL + p2p_product.get_h5_url
                            else:
                                p2p_dict['url'] = settings.WLB_URL + p2p_product.get_pc_url

                            p2p_dict['amount'] = float(p2p_record.amount),
                            p2p_dict['investtime'] = utc_to_local_timestamp(p2p_record.created_at)
                            p2p_dict['period'] = p2p_product.period
                            p2p_dict['unit'] = p_type
                            p2p_dict['rate'] = rate

                            p2p_list.append(p2p_dict)

                        ret['list'] = p2p_list
                        ret['status'] = 0
                        ret['username'] = channel_account
                        ret['usernamep'] = self.request.POST.get('usernamep', None)
                        ret['level'] = 0
                    else:
                        ret = {
                            'status': 1,
                            'errmsg': u"用户不存在"
                        }
                else:
                    ret = {
                        'status': 1,
                        'errmsg': u"签名错误"
                    }
            else:
                ret = {
                    'status': 1,
                    'errmsg': u"非法请求"
                }
        else:
            ret = {
                'status': 1,
                'errmsg': u"非法请求"
            }

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class TanLiuLiuAllUserInvestmentQuery(APIView):
    """
    弹66用户投资查询接口
    """
    permission_classes = ()

    def check_sign(self):
        channel_name = str(self.request.POST.get('from', None))
        username = self.request.POST.get('username', None)
        usernamep = self.request.POST.get('usernamep', None)
        timestamp = self.request.POST.get('timestamp', None)
        sign = self.request.POST.get('sign', None)
        starttime = self.request.POST.get('starttime', None)
        endtime = self.request.POST.get('endtime', None)
        if channel_name and username and usernamep and timestamp and sign and starttime and endtime:
            from hashlib import md5
            sign = md5(md5(t).hexdigest() + settings.XICAI_CLIENT_SECRET).hexdigest()
            if token == sign:
                return True

    def post(self, request):

        if self.check_sign():

            page = int(self.request.POST.get('page', 1))
            page_size = int(self.request.POST.get('pagesize', 10))
            p2p_list = []
            ret = dict()

            starttime = self.request.POST.get('starttime', None)
            endtime = self.request.POST.get('endtime', None)

            binds = Binding.objects.filter((Q(btype=u'tan66')) & Q(created_at__gte=starttime) & Q(created_at__lte=endtime))
            users = [b.user for b in binds]
            p2ps = P2PEquity.objects.filter(user__in=users)

            ret['total'] = p2ps.count()

            # 获取总页数, 和页数不对处理
            com_page = len(p2ps) / page_size + 1

            if page > com_page:
                page = com_page
            if page < 1:
                page = 1

            # 获取到对应的页数的所有用户
            if len(p2ps) / page_size >= page:
                p2ps = p2ps[(page - 1) * page_size: page * page_size]
            else:
                p2ps = p2ps[(page - 1) * page_size:]

            for p2p in p2ps:
                p2pproduct = p2p.product

                reward = Decimal.from_float(0).quantize(Decimal('0.0000'), 'ROUND_DOWN')
                if p2pproduct.activity:
                    reward = p2pproduct.activity.rule.rule_amount.quantize(Decimal('0.0000'), 'ROUND_DOWN')

                rate = p2pproduct.expected_earning_rate + float(reward * 100)

                rate = Decimal.from_float(rate / 100).quantize(Decimal('0.0000'))

                matches = re.search(u'日计息', p2pproduct.pay_method)
                if matches and matches.group():
                    p_type = 0
                else:
                    p_type = 1

                p2p_dict = dict()
                p2p_dict['oid'] = p2p.id
                p2p_dict['bid'] = p2pproduct.id
                p2p_dict['title'] = p2pproduct.name
                p2p_dict['url'] = "https://{}/p2p/detail/{}".format(request.get_host(), p2pproduct.id)
                p2p_dict['amount'] = p2p.equity
                p2p_dict['investtime'] = p2p.created_at
                p2p_dict['period'] = p2pproduct.period
                p2p_dict['unit'] = p_type
                p2p_dict['rate'] = rate

                p2p_list.append(p2p_dict)

            ret['list'] = p2p_list
            ret['status'] = 0
            ret['username'] = self.request.POST.get('username', None)
            ret['usernamep'] = self.request.POST.get('usernamep', None)
            ret['level'] = 0

        else:
            ret = {
                'status': 1,
                'errmsg': u"没有权限访问"
            }
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))