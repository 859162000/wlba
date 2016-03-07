#!/usr/bin/env python
# encoding:utf-8

import json
import logging
import hashlib
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework.views import APIView
from wanglibao_account.cooperation import CoopRegister, get_client, get_uid_for_coop, CoopSessionProcessor
from wanglibao_p2p.models import P2PRecord
from django.utils import timezone
from wanglibao_rest.utils import has_binding_for_bid, get_coop_binding_for_phone
from django.http import Http404
from marketing.models import Channels
from marketing.utils import get_channel_record
from django.conf import settings
from wanglibao_account.utils import create_user
from wanglibao_p2p.forms import PurchaseForm
from wanglibao_pay.forms import RechargeForm
from wanglibao_pay.models import PayInfo
from .forms import CoopDataDispatchForm
from marketing.forms import ChannelForm
from wanglibao_account.forms import UserRegisterForm, UserForm


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

    def check_sign(self, client_id, phone, key, sign):
        local_sign = hashlib.md5(str(client_id) + key + str(phone)).hexdigest()
        if local_sign == sign:
            sign_is_ok = True
        else:
            sign_is_ok = False

        return sign_is_ok

    def post(self, request, **kwargs):
        channel_code = request.GET.get('promo_token', None)
        if channel_code:
            channel = get_channel_record(channel_code)
            if channel:
                sign = request.session.get('sign')
                print sign
                if sign:
                    client_id = request.session.get('client_id')
                    if client_id:
                        client = get_client(channel_code)
                        if client:
                            phone = request.session.get('phone')
                            if phone:
                                if self.check_sign(client_id, phone, client.client_secret, sign):
                                    binding = get_coop_binding_for_phone(channel_code, phone)
                                    user = User.objects.filter(wanglibaouserprofile__phone=phone).first()
                                    if binding and user:
                                        response_data = {
                                            'user_id': binding.bid,
                                            'ret_code': 10000,
                                            'message': u'该号已注册'
                                        }
                                    elif not user:
                                        response_data = {
                                            'user_id': None,
                                            'ret_code': 10001,
                                            'message': u'该号未注册'
                                        }
                                    else:
                                        response_data = {
                                            'user_id': None,
                                            'ret_code': 10002,
                                            'message': u'该号已注册，非本渠道用户'
                                        }

                                    return HttpResponse(json.dumps(response_data), status=200, content_type='application/json')
                                else:
                                    response_data = {
                                        'user_id': None,
                                        'ret_code': 10008,
                                        'message': u'无效签名'
                                    }
                            else:
                                response_data = {
                                    'user_id': None,
                                    'ret_code': 10007,
                                    'message': u'手机号不存在'
                                }
                        else:
                            response_data = {
                                'user_id': None,
                                'ret_code': 10006,
                                'message': u'无效客户端id不存在'
                            }
                    else:
                        response_data = {
                            'user_id': None,
                            'ret_code': 10005,
                            'message': u'客户端id参数不存在'
                        }
                else:
                    response_data = {
                        'user_id': None,
                        'ret_code': 10004,
                        'message': u'签名参数不存在'
                    }
            else:
                response_data = {
                    'user_id': None,
                    'ret_code': 10003,
                    'message': u'无效promo_token'
                }
        else:
            return Http404(u'页面不存在')

        CoopSessionProcessor(request).all_processors_for_session(1)

        return HttpResponse(json.dumps(response_data), status=200, content_type='application/json')


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
            response_data = self.parase_form_error(form.error)

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
            user = create_user(user_id, phone)
            if user:
                # FixMe，异步调用渠道数据回调任务
                try:
                    CoopRegister(btype, bid, client_id, order_id).all_processors_for_user_register(user)
                except Exception, e:
                    logger.info("process_register raise error: %s" % e)

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
        form = RechargeForm(req_data)
        if form.is_valid():
            pay_info = PayInfo()
            pay_info.order_id = form.cleaned_data['order_id']
            pay_info.amount = form.cleaned_data['amount']
            pay_info.user = form.cleaned_data['user_id']
            pay_info.recharge_at = form.cleaned_data['recharge_at']
            pay_info.status = form.cleaned_data['status']
            pay_info.save()
            # FixMe,异步回调给第三方
            response_data = {
                'ret_code': 10000,
                'message': 'success',
            }
        else:
            response_data = self.parase_form_error(form.error)

        return response_data

    def process_purchase(self, req_data):
        form = PurchaseForm(req_data)
        if form.is_valid():
            p2p_record = P2PRecord()
            p2p_record.catalog = form.cleaned_data['catalog']
            p2p_record.order_id = form.cleaned_data['order_id']
            p2p_record.amount = form.cleaned_data['amount']
            p2p_record.product = form.cleaned_data['product_id']
            p2p_record.user = form.cleaned_data['user_id']
            p2p_record.purchase_at = form.cleaned_data['purchase_at']
            p2p_record.save()
            # FixMe,异步回调给第三方
            response_data = {
                'ret_code': 10000,
                'message': 'success',
            }
        else:
            response_data = self.parase_form_error(form.error)

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
            response_data = self.parase_form_error(form.error)

        return response_data

    def process_validate(self, req_data):
        form = UserForm(req_data)
        if form.is_valid():
            user = form.cleaned_data['user_id']
            user.wanglibaouserprofile.id_is_valid = True
            user.wanglibaouserprofile.id_valid_time = timezone.now()
            user.wanglibaouserprofile.save()
            response_data = {
                'ret_code': 10000,
                'message': 'success',
            }
            # FixMe,异步回调给第三方
        else:
            response_data = self.parase_form_error(form.error)

        return response_data

    def process_withdraw(self, req_data):
        pass

    def process_amortization(self, req_data):
        pass

    def post(self, request):
        req_data = request.POST
        logger.info("channel data dispatch processing with %s" % req_data)
        form = CoopDataDispatchForm(req_data)
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
                        response_data = processer(req_data)
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
            # sfsfw232342sdfsfsdfsfsdgddf

        logger.info('channel data dispatch process result:%s' % response_data['message'])

        return HttpResponse(json.dumps(response_data), status=200, content_type='application/json')
