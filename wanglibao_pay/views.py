# -*- coding: utf-8 -*-

import logging
import re
import socket
import json

from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib.auth.decorators import permission_required, login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import HttpResponseBadRequest
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from order.models import Order
from order.utils import OrderHelper
from wanglibao_account.cooperation import CoopRegister
from wanglibao_account.models import IdVerification
from wanglibao_margin.exceptions import MarginLack
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_pay.exceptions import ThirdPayError, ManyCardException, AbnormalCardException
from wanglibao_pay.models import Bank, Card, PayResult, PayInfo, WithdrawCard, WithdrawCardRecord, \
    WhiteListCard, BlackListCard
from wanglibao_pay.huifu_pay import HuifuPay, SignException
from wanglibao_pay import third_pay, trade_record
from wanglibao_p2p.models import P2PRecord
import decimal
from wanglibao_pay.pay import YeeProxyPay, PayOrder, YeeProxyPayCallbackMessage
from wanglibao_pay.serializers import CardSerializer
from wanglibao_pay.third_pay import TheOneCard
from wanglibao_pay.util import get_client_ip, fmt_two_amount
from wanglibao_pay import util
from wanglibao_profile.backends import require_trade_pwd
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_rest.utils import split_ua
from wanglibao_sms import messages
from wanglibao_sms.tasks import send_messages
from wanglibao_account import message as inside_message
from wanglibao.const import ErrorNumber
from wanglibao_sms.utils import validate_validation_code
from django.conf import settings
from wanglibao_announcement.utility import AnnouncementAccounts
# from wanglibao_account.forms import verify_captcha
from fee import WithdrawFee
import datetime
from wanglibao_rest import utils as rest_utils
from weixin.models import WeixinUser
from wanglibao_rest.common import DecryptParmsAPIView
from marketing.tools import withdraw_submit_ok

logger = logging.getLogger(__name__)
TWO_PLACES = decimal.Decimal(10) ** -2


class BankListView(TemplateView):
    """
    pc端使用的银行列表页
    """
    template_name = 'pay_banks.jade'

    def get_context_data(self, **kwargs):
        context = super(BankListView, self).get_context_data(**kwargs)

        default_bank = Bank.get_deposit_banks().filter(
            name=self.request.user.wanglibaouserprofile.deposit_default_bank_name).first()

        context.update({
            'default_bank': default_bank,
            'banks': Bank.get_deposit_banks()[:14],
            'announcements': AnnouncementAccounts
        })
        return context


class BankListForRegisterView(BankListView):
    """
    pc端使用的银行列表页，新的用户注册流程需要用户在注册之后就充值，这个页面给注册时的充值使用
    """
    template_name = 'register_second.jade'


class PayView(TemplateView):
    template_name = 'pay_jump.jade'

    def post(self, request):
        # if not request.user.wanglibaouserprofile.id_is_valid:
        #     return self.render_to_response({
        #         'message': u'请先进行实名认证'
        #     })
        # form = dict()
        # message = ''
        # try:
        #     amount_str = request.POST.get('amount', '')
        #     amount = decimal.Decimal(amount_str). \
        #         quantize(TWO_PLACES, context=decimal.Context(traps=[decimal.Inexact]))
        #     amount_str = str(amount)
        #     if amount <= 0:
        #         raise decimal.DecimalException()
        #
        #     gate_id = request.POST.get('gate_id', '')
        #     bank = Bank.objects.get(gate_id=gate_id)
        #
        #     # Store this as the default bank
        #     request.user.wanglibaouserprofile.deposit_default_bank_name = bank.name
        #     request.user.wanglibaouserprofile.save()
        #
        #     pay_info = PayInfo()
        #     pay_info.amount = amount
        #     pay_info.total_amount = amount
        #     pay_info.type = PayInfo.DEPOSIT
        #     pay_info.status = PayInfo.INITIAL
        #     pay_info.user = request.user
        #     pay_info.bank = bank
        #     pay_info.channel = "huifu"
        #     pay_info.request_ip = get_client_ip(request)
        #
        #     order = OrderHelper.place_order(request.user, Order.PAY_ORDER, pay_info.status,
        #                                     pay_info=model_to_dict(pay_info))
        #     pay_info.order = order
        #     pay_info.save()
        #
        #     post = {
        #         'OrdId': pay_info.pk,
        #         'GateId': gate_id,
        #         'OrdAmt': amount_str
        #     }
        #
        #     pay = HuifuPay()
        #     form = pay.pay(post)
        #     pay_info.request = str(form)
        #     pay_info.status = PayInfo.PROCESSING
        #     pay_info.save()
        #     OrderHelper.update_order(order, request.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
        #
        #     # 处理第三方渠道的用户充值回调
        #     CoopRegister(request).process_for_recharge(request.user)
        # except decimal.DecimalException:
        #     message = u'金额格式错误'
        # except Bank.DoesNotExist:
        #     message = u'请选择有效的银行'
        # except (socket.error, SignException) as e:
        #     message = PayResult.RETRY
        #     pay_info.status = PayInfo.FAIL
        #     pay_info.error_message = str(e)
        #     pay_info.save()
        #     OrderHelper.update_order(order, request.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
        #     logger.fatal('sign error! order id: ' + str(pay_info.pk) + ' ' + str(e))
        #
        # context = {
        #     'message': message,
        #     'form': form
        # }

        # gate_id = request.POST.get('gate_id', '')
        # bank = Bank.objects.get(gate_id=gate_id)
        # pay_channel_class = get_pc_channel_class(bank.pc_channel)
        #
        # pay_channel = pay_channel_class()
        # result = pay_channel.pre_pay(request)
        # return self.render_to_response(result)
        logger.info('web_pay_request_para:' + str(request.POST))

        try:
            user = request.user
            amount = fmt_two_amount(request.POST.get('amount'))
            gate_id = request.POST.get('gate_id')
            request_ip = get_client_ip(request)
            device_type = split_ua(request)['device_type']
            channel = PayOrder.get_bank_and_channel(gate_id, device_type)[1]
        except:
            logger.exception('third_pay_error')
            result = {'message': '参数错误'}
            return self.render_to_response(result)

        if channel == 'yeepay':
            result = YeeProxyPay().proxy_pay(user, amount,  gate_id,  request_ip, device_type)
        else:
            result = HuifuPay().pre_pay(request)
        return self.render_to_response(result)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PayView, self).dispatch(request, *args, **kwargs)


class PayCompleteView(TemplateView):
    template_name = 'pay_complete.jade'

    def post(self, request, *args, **kwargs):
        result = HuifuPay.handle_pay_result(request)
        amount = request.POST.get('OrdAmt', '')

        return self.render_to_response({
            'result': result,
            'amount': amount
        })

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PayCompleteView, self).dispatch(request, *args, **kwargs)


class PayCallback(View):
    def post(self, request, *args, **kwargs):
        HuifuPay.handle_pay_result(request)
        order_id = request.POST.get('OrdId', '')

        return HttpResponse('RECV_ORD_ID_' + order_id)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PayCallback, self).dispatch(request, *args, **kwargs)


class YeeProxyPayCompleteView(TemplateView):
    template_name = 'pay_complete.jade'

    def _process(self, request):
        try:
            request_ip = get_client_ip(request)
            if request.method == 'GET':
                message_dict = request.GET
            elif request.method == 'POST':
                message_dict = request.POST
            pay_message = YeeProxyPayCallbackMessage().parse_message(message_dict, request_ip)
            result = YeeProxyPay().proxy_pay_callback(pay_message, request)
            amount = pay_message.amount
        except ThirdPayError, e:
            logger.exception('third_pay_error')
            result = {'ret_code': e.code}
            amount = 0
        return result, amount

    @method_decorator(login_required(login_url='/accounts/login'))
    def post(self, request, *args, **kwargs):
        # result = HuifuPay.handle_pay_result(request)
        # amount = request.POST.get('OrdAmt', '')
        #
        # return self.render_to_response({
        #     'result': result,
        #     'amount': amount
        # })
        logger.info('web_pay_thirdpay_get_request_para'+str(request.GET))
        result, amount = self._process(request)

        return self.render_to_response({
            'result': '充值成功' if result['ret_code'] == 0 else '充值失败',
            'amount': amount
            })

    def get(self, request, *args, **kwargs):
        logger.info('web_pay_thirdpay_post_request_para'+str(request.POST))
        self._process(request)
        return HttpResponse('success')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(YeeProxyPayCompleteView, self).dispatch(request, *args, **kwargs)


class WithdrawView(TemplateView):
    template_name = 'withdraw.jade'

    def get_context_data(self, **kwargs):
        cards = Card.objects.filter(user=self.request.user).order_by("-is_default").select_related()
        banks = Bank.get_withdraw_banks()

        # 提现管理费费率
        fee_misc = WithdrawFee()
        fee_config = fee_misc.get_withdraw_fee_config()
        withdraw_count = fee_misc.get_withdraw_count(user=self.request.user)
        return {
            'cards': cards,
            'banks': banks,
            'user_profile': self.request.user.wanglibaouserprofile,
            'margin': self.request.user.margin.margin,
            'uninvested': self.request.user.margin.uninvested,
            'withdraw_count': withdraw_count,
            'fee': fee_config,
            'announcements': AnnouncementAccounts
        }

    def dispatch(self, request, *args, **kwargs):
        if request.user.wanglibaouserprofile.frozen:
            return HttpResponseRedirect('/')
        return super(WithdrawView, self).dispatch(request, *args, **kwargs)


class WithdrawCompleteView(TemplateView):
    template_name = 'withdraw_complete.jade'

    @method_decorator(transaction.atomic)
    def post(self, request, *args, **kwargs):
        #result, message = verify_captcha(request.POST)
        #if not result:
        #    return self.render_to_response({
        #        'result': message
        #    })

        user = request.user
        if not user.wanglibaouserprofile.id_is_valid:
            return self.render_to_response({
                'result': u'请先进行实名认证'
            })
        if user.wanglibaouserprofile.frozen:
            return self.render_to_response({
                'result': u'账户已冻结!请联系网利宝客服:4008-588-066'
            })
        phone = user.wanglibaouserprofile.phone
        code = request.POST.get('validate_code', '')
        status, message = validate_validation_code(phone, code)
        if status != 200:
            return self.render_to_response({
                # Modify by hb on 2015-12-02
                #'result': u'短信验证码输入错误'
                'result': message
            })

        result = PayResult.WITHDRAW_SUCCESS

        try:
            card_id = request.POST.get('card_id', '')
            card = Card.objects.get(pk=card_id, user=user)
            card_no = card.no

            # 检测银行卡是否在黑名单中
            black_list = BlackListCard.objects.filter(card_no=card_no).first()
            if black_list and black_list.user != user:
                raise AbnormalCardException

            # 检查白名单
            white_list = WhiteListCard.objects.filter(user=user, card_no=card_no).first()
            if not white_list:
                # 增加银行卡号检测功能,检测多张卡
                card_count = Card.objects.filter(no=card_no).count()
                if card_count > 1:
                    raise ManyCardException

                # 检测银行卡在以前的提现记录中是否为同一个用户
                payinfo_record = PayInfo.objects.filter(card_no=card_no).order_by('-create_time').first()
                if payinfo_record:
                    if payinfo_record.user != user:
                        raise AbnormalCardException

            amount_str = request.POST.get('amount', '')
            amount = decimal.Decimal(amount_str). \
                quantize(TWO_PLACES, context=decimal.Context(traps=[decimal.Inexact]))
            margin = user.margin.margin  # 账户余额
            uninvested = user.margin.uninvested  # 充值未投资金额

            # 获取费率配置
            fee_misc = WithdrawFee()
            fee_config = fee_misc.get_withdraw_fee_config()

            # 计算提现费用 手续费 + 资金管理费
            # 提现最大最小金额判断
            if amount > fee_config.get('max_amount') or amount <= 0:
                raise decimal.DecimalException
            if amount < fee_config.get('min_amount'):
                if amount != margin:
                    raise decimal.DecimalException
            # 获取计算后的费率
            fee, management_fee, management_amount = fee_misc.get_withdraw_fee(user, amount, margin, uninvested)

            actual_amount = amount - fee - management_fee  # 实际到账金额
            if actual_amount <= 0:
                raise decimal.DecimalException

            # 检测个别银行的单笔提现限额,如民生银行
            bank_limit = util.handle_withdraw_limit(card.bank.withdraw_limit)
            bank_max_amount = bank_limit.get('bank_max_amount', 0)
            if bank_max_amount:
                if amount > bank_max_amount:
                    raise decimal.DecimalException

            pay_info = PayInfo()
            pay_info.amount = actual_amount
            pay_info.fee = fee
            pay_info.management_fee = management_fee
            pay_info.management_amount = management_amount
            pay_info.total_amount = amount
            pay_info.type = PayInfo.WITHDRAW
            pay_info.user = user
            pay_info.card_no = card.no
            pay_info.account_name = user.wanglibaouserprofile.name
            pay_info.bank = card.bank
            pay_info.request_ip = get_client_ip(request)
            pay_info.status = PayInfo.ACCEPTED

            order = OrderHelper.place_order(user, Order.WITHDRAW_ORDER, pay_info.status,
                                            pay_info=model_to_dict(pay_info))

            pay_info.order = order
            keeper = MarginKeeper(user, pay_info.order.pk)
            margin_record = keeper.withdraw_pre_freeze(amount, uninvested=management_amount)
            pay_info.margin_record = margin_record

            pay_info.save()
            name = user.wanglibaouserprofile.name or u'用户'
            withdraw_submit_ok.apply_async(kwargs={
                "user_id": user.id,
                "user_name": name,
                "phone": user.wanglibaouserprofile.phone,
                "amount": amount,
                "bank_name": card.bank.name
            })
        except decimal.DecimalException:
            result = u'提款金额在0～{}之间'.format(fee_config.get('max_amount'))
        except Card.DoesNotExist:
            result = u'请选择有效的银行卡'
        except ManyCardException:
            result = u'银行卡号存在重复，请尝试其他银行卡号码，如非本人操作请联系客服'
        except AbnormalCardException:
            result = u'银行卡号与身份信息存在异常, 如非本人操作请联系客服'
        except MarginLack as e:
            result = u'余额不足'
            pay_info.error_message = str(e)
            pay_info.status = PayInfo.FAIL
            pay_info.save()

        # return self.render_to_response({
        #     'result': result
        # })
        return HttpResponseRedirect(reverse('withdraw-complete-result', kwargs={'result': result}))


class WithdrawRedirectView(TemplateView):
    template_name = 'withdraw_complete.jade'

    def get_context_data(self, result, **kwargs):
        return {
            "result": result
        }


class WithdrawCallback(View):
    def post(self, request, *args, **kwargs):
        HuifuPay.handle_withdraw_result(request.POST.dict())
        order_id = request.POST.get('OrdId', '')
        return HttpResponse('RECV_ORD_ID_' + order_id)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WithdrawCallback, self).dispatch(request, *args, **kwargs)


class CardViewSet(ModelViewSet):
    model = Card
    serializer = CardSerializer
    throttle_classes = (UserRateThrottle,)
    permission_classes = IsAuthenticated,

    @property
    def allowed_methods(self):
        return 'POST'

    def create(self, request):
        card = Card()
        card.user = request.user
        no = request.DATA.get('no', '')
        if no:
            card.no = no
        else:
            return Response({
                                "message": u"银行账号不能为空",
                                'error_number': ErrorNumber.card_number_error
                            }, status=status.HTTP_400_BAD_REQUEST)

        is_default = request.DATA.get('is_default', False)

        if is_default == 'true':
            card.is_default = True
        elif is_default == 'false':
            card.is_default = False
        else:
            return Response({
                                "message": u"设置是否默认银行卡错误",
                                'error_number': ErrorNumber.card_isdefault_error
                            }, status=status.HTTP_400_BAD_REQUEST)

        if not re.match('^[\d]{0,25}$', card.no):
            return Response({
                                "message": u"银行账号超过长度",
                                'error_number': ErrorNumber.form_error
                            }, status=status.HTTP_400_BAD_REQUEST)

        bank_id = request.DATA.get('bank', '')

        exist_cards = Card.objects.filter(no=card.no)
        exist_cards1 = Card.objects.filter(user=card.user, no__startswith=card.no[:6], no__endswith=card.no[-4:]).first()
        if exist_cards or exist_cards1:
            return Response({
                                "message": u"您输入的银行卡号已绑定，请尝试其他银行卡号码，如非本人操作请联系客服",
                                'error_number': ErrorNumber.duplicate
                            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            card.bank = Bank.objects.get(pk=bank_id)
        except:
            return Response({
                                "message": u"没有找到该银行",
                                'error_number': ErrorNumber.not_find
                            }, status=status.HTTP_400_BAD_REQUEST)

        # passport user
        if not request.user.wanglibaouserprofile.id_number[0].isdigit():
            card.is_bind_yee = True

        card.save()

        try:
            # 处理第PC三方用户绑卡回调
            CoopRegister(request).process_for_binding_card(request.user)
        except Exception, e:
            logger.error(e)

        return Response({
            'id': card.pk,
            'no': card.no,
            'bank_name': card.bank.name
        })

    def destroy(self, request, pk=None):
        card_id = request.DATA.get('card_id', '')
        card = Card.objects.filter(id=card_id, user=self.request.user).first()
        if card:
            # 将删除的银行卡添加到异常银行卡名单中
            black_list = BlackListCard()
            black_list.user = self.request.user
            black_list.card_no = card.no
            black_list.message = u'删除银行卡,手机号:{}'.format(self.request.user.wanglibaouserprofile.phone)
            black_list.ip = get_client_ip(request)
            black_list.save()

            # 删除银行卡
            card.delete()
            return Response({
                'id': card_id
            })
        else:
            return Response({
                                "message": u"查不到银行卡，请联系管理员",
                                'error_number': ErrorNumber.duplicate
                            }, status=status.HTTP_400_BAD_REQUEST)


class WithdrawTransactions(TemplateView):
    """ for admin
    """
    template_name = 'withdraw_transactions.jade'

    def post(self, request):
        action = request.POST.get('action')
        uuids_param = request.POST.get('transaction_uuids', '')
        uuids = re.findall(r'[\w\-_]+', uuids_param)
        payinfos = PayInfo.objects.filter(uuid__in=uuids, type='W').order_by('create_time')

        # These are the uuids exists in db for real
        uuids_param = ",".join([payinfo.uuid for payinfo in payinfos])

        if action == 'preview' or action is None:
            return self.render_to_response(
                {
                    'payinfos': payinfos,
                    'total_amount': payinfos.aggregate(Sum("amount"))['amount__sum'],
                    'transaction_uuids': uuids_param
                }
            )
        elif action == 'confirm':
            for payinfo in payinfos:
                with transaction.atomic():
                    if payinfo.status != PayInfo.ACCEPTED and payinfo.status != PayInfo.PROCESSING:
                        logger.info("The withdraw status [%s] not in %s or %s, ignore it" % (
                        payinfo.status, PayInfo.ACCEPTED, PayInfo.PROCESSING))
                        continue

                    amount = payinfo.amount
                    fee = payinfo.fee
                    management_fee = payinfo.management_fee
                    management_amount = payinfo.management_amount

                    marginKeeper = MarginKeeper(payinfo.user)
                    total_amount = amount + fee + management_fee
                    marginKeeper.withdraw_ack(total_amount, uninvested=management_amount)

                    payinfo.status = PayInfo.SUCCESS
                    payinfo.confirm_time = timezone.now()
                    payinfo.save()

                    # 给提现记录表中的信息同步进行确认,同时将提现的费用充值到网利宝的公司提现账户

                    if fee > 0 or management_fee > 0:
                        fee_total_amount = fee + management_fee
                        withdraw_card = WithdrawCard.objects.filter(is_default=True).first()
                        withdraw_card.amount += fee_total_amount
                        withdraw_card.save()

                        # 将提现信息单独记录到提现费用记录表中
                        withdraw_card = WithdrawCard.objects.filter(is_default=True).first()
                        if withdraw_card:
                            withdraw_card_record = WithdrawCardRecord()
                            withdraw_card_record.type = PayInfo.WITHDRAW
                            withdraw_card_record.amount = amount
                            withdraw_card_record.fee = fee
                            withdraw_card_record.management_fee = management_fee
                            withdraw_card_record.management_amount = management_amount
                            withdraw_card_record.withdrawcard = withdraw_card
                            withdraw_card_record.payinfo = payinfo
                            withdraw_card_record.user = payinfo.user
                            withdraw_card_record.status = PayInfo.SUCCESS
                            withdraw_card_record.message = u'用户提现费用存入'
                            withdraw_card_record.save()

                    # 取款确认时要检测该次提现是否是真正的在每个月的免费次数之内,如果是还需要将已扣除的费用返还给用户(仅限手续费)
                    give_back = False
                    if fee > 0:
                        fee_misc = WithdrawFee()
                        fee_config = fee_misc.get_withdraw_fee_config()
                        withdraw_count = fee_misc.get_withdraw_success_count(payinfo.user)
                        free_times = fee_config['fee']['free_times_per_month']
                        if withdraw_count <= free_times:
                            give_back = True

                    if give_back:
                        # 1.给用户返还手续费
                        marginKeeper.deposit(fee, description=u'返还提现免费次数之内的手续费:{}元'.format(fee), catalog=u"返还手续费")

                        # 2.从网利宝提现账户中减去手续费
                        withdraw_card = WithdrawCard.objects.filter(is_default=True).first()
                        withdraw_card.amount -= fee
                        withdraw_card.save()
                        
                        # 将提现信息单独记录到提现费用记录表中
                        withdraw_card_record = WithdrawCardRecord()
                        withdraw_card_record.type = PayInfo.WITHDRAW
                        withdraw_card_record.amount = fee
                        withdraw_card_record.fee = fee
                        withdraw_card_record.management_fee = 0
                        withdraw_card_record.management_amount = 0
                        withdraw_card_record.withdrawcard = withdraw_card
                        withdraw_card_record.payinfo = payinfo
                        withdraw_card_record.user = payinfo.user
                        withdraw_card_record.status = PayInfo.SUCCESS
                        withdraw_card_record.message = u'用户提现费用返还'
                        withdraw_card_record.save()

                    # 发站内信
                    title, content = messages.msg_withdraw_success(timezone.now(), payinfo.amount)
                    inside_message.send_one.apply_async(kwargs={
                        "user_id": payinfo.user_id,
                        "title": title,
                        "content": content,
                        "mtype": "withdraw"
                    })
                    send_messages.apply_async(kwargs={
                        "phones": [payinfo.user.wanglibaouserprofile.phone],
                        "messages": [messages.withdraw_confirmed(payinfo.user.wanglibaouserprofile.name, amount)]
                    })
            return HttpResponse({
                u"所有的取款请求已经处理完毕 %s" % uuids_param
            })

    @method_decorator(permission_required('wanglibao_pay.change_payinfo'))
    def dispatch(self, request, *args, **kwargs):
        """
        Only user with change payinfo permission can call this view
        """
        return super(WithdrawTransactions, self).dispatch(request, *args, **kwargs)


class WithdrawRollback(TemplateView):
    template_name = 'withdraw_rollback.jade'

    def post(self, request):
        uuid = request.POST.get('uuid', '')
        error_message = request.POST.get('error_message', '')
        #try:
        #    payinfo = PayInfo.objects.get(uuid=uuid, type='W')
        #except PayInfo.DoesNotExist:
        #    return HttpResponse({
        #        u"没有找到 %s 该记录" % uuid
        #    })

        payinfo = PayInfo.objects.filter(uuid=uuid, type='W').first()
        if not payinfo:
            return HttpResponse({u"没有找到 %s 该记录" % uuid})

        if payinfo.status == PayInfo.FAIL or payinfo.status == PayInfo.SUCCESS:
            logger.info("The withdraw status [%s] already process , ignore it" % uuid)
            return HttpResponse({u"该%s 请求已经处理过,请勿重复处理" % uuid})

        marginKeeper = MarginKeeper(payinfo.user)
        # 提现审核失败回滚时需要将扣除的各手续费返还
        total_amount = payinfo.amount + payinfo.fee + payinfo.management_fee
        marginKeeper.withdraw_rollback(total_amount, error_message, uninvested=payinfo.management_amount)
        payinfo.status = PayInfo.FAIL
        payinfo.error_message = error_message
        payinfo.confirm_time = None
        payinfo.save()

        # 短信通知添加用户名
        name = payinfo.user.wanglibaouserprofile.name or u'用户'

        send_messages.apply_async(kwargs={
            "phones": [payinfo.user.wanglibaouserprofile.phone],
            "messages": [messages.withdraw_failed(name, error_message)]
        })

        title, content = messages.msg_withdraw_fail(timezone.now(), payinfo.amount)
        inside_message.send_one.apply_async(kwargs={
            "user_id": payinfo.user.id,
            "title": title,
            "content": content,
            "mtype": "withdraw"
        })

        return HttpResponse({
            u"该 %s 请求已经处理完毕" % uuid
        })

    @method_decorator(permission_required('wanglibao_pay.change_payinfo'))
    def dispatch(self, request, *args, **kwargs):
        """
        Only user with change payinfo permission can call this view
        """
        return super(WithdrawRollback, self).dispatch(request, *args, **kwargs)


class AdminTransaction(TemplateView):
    template_name = 'admin_transaction.jade'


class AdminTransactionP2P(TemplateView):
    template_name = 'admin_transaction_p2p.jade'

    def get_context_data(self, **kwargs):

        phone = self.request.GET.get('phone', None)
        if phone:
            try:
                user_profile = WanglibaoUserProfile.objects.get(phone=phone)
            except WanglibaoUserProfile.DoesNotExist:
                return {
                    'message': u"手机号 %s 有误，请输入合法的手机号" % phone
                }
            except Exception:
                return {
                    'message': u"手机号不能为空"
                }

            trade_records = P2PRecord.objects.filter(user=user_profile.user)
            pager = Paginator(trade_records, 20)
            page = self.request.GET.get('page')
            if not page:
                page = 1
            trade_records = pager.page(page)

            return {
                "pay_records": trade_records,
                "phone": phone

            }
        else:
            return {
                'message': u"手机号不能为空"
            }

    @method_decorator(permission_required('wanglibao_pay.change_payinfo', login_url='/' + settings.ADMIN_ADDRESS))
    def dispatch(self, request, *args, **kwargs):
        """
        Only user with change payinfo permission can call this view
        """
        return super(AdminTransactionP2P, self).dispatch(request, *args, **kwargs)


class AdminTransactionWithdraw(TemplateView):
    template_name = 'admin_transaction_withdraw.jade'


    def get_context_data(self, **kwargs):
        phone = self.request.GET.get('phone', None)

        if phone:
            try:
                user_profile = WanglibaoUserProfile.objects.get(phone=phone)
            except WanglibaoUserProfile.DoesNotExist:
                return {
                    'message': u"手机号 %s 有误，请输入合法的手机号" % phone
                }
            except Exception:
                return {
                    'message': u"手机号不能为空"
                }

            pay_records = PayInfo.objects.filter(user=user_profile.user, type=PayInfo.WITHDRAW)
            pager = Paginator(pay_records, 20)
            page = self.request.GET.get('page')

            if not page:
                page = 1
            pay_records = pager.page(page)

            return {
                "pay_records": pay_records,
                "phone": phone
            }
        else:
            return {
                'message': u"手机号不能为空"
            }

    @method_decorator(permission_required('wanglibao_pay.change_payinfo', login_url='/' + settings.ADMIN_ADDRESS))
    def dispatch(self, request, *args, **kwargs):
        """
        Only user with change payinfo permission can call this view
        """
        return super(AdminTransactionWithdraw, self).dispatch(request, *args, **kwargs)


class AdminTransactionDeposit(TemplateView):
    template_name = 'admin_transaction_deposit.jade'

    def get_context_data(self, **kwargs):
        phone = self.request.GET.get('phone', None)
        if phone:
            try:
                user_profile = WanglibaoUserProfile.objects.get(phone=phone)
            except WanglibaoUserProfile.DoesNotExist:
                return {
                    'message': u"手机号 %s 有误，请输入合法的手机号" % phone
                }
            except Exception:
                return {
                    'message': u"手机号不能为空"
                }

            pay_records = PayInfo.objects.filter(user=user_profile.user, type=PayInfo.DEPOSIT)
            pager = Paginator(pay_records, 20)
            page = self.request.GET.get('page')

            if not page:
                page = 1
            pay_records = pager.page(page)

            return {
                "pay_records": pay_records,
                "phone": phone
            }
        else:
            return {
                'message': u"手机号不能为空"
            }

    @method_decorator(permission_required('wanglibao_pay.change_payinfo', login_url='/' + settings.ADMIN_ADDRESS))
    def dispatch(self, request, *args, **kwargs):
        """
        Only user with change payinfo permission can call this view
        """
        return super(AdminTransactionDeposit, self).dispatch(request, *args, **kwargs)


# 易宝支付创建订单接口
class YeePayAppPayView(DecryptParmsAPIView):
    permission_classes = (IsAuthenticated, )

    @require_trade_pwd
    def post(self, request):
        yeepay = third_pay.YeePay()
        result = yeepay.app_pay(request)

        # if result['ret_code'] == 0:
        #     try:
        #         # 处理第三方用户充值回调
        #         CoopRegister(request).process_for_recharge(request.user)
        #     except Exception, e:
        #         logger.error(e)

        return Response(result)

#易宝支付回调
class YeePayAppPayCallbackView(APIView):
    permission_classes = ()

    def post(self, request):
        yeepay = third_pay.YeePay()
        request.GET = request.DATA
        result = yeepay.pay_callback(request)
        return Response(result)

#易宝支付同步回调
class YeePayAppPayCompleteView(TemplateView):
    template_name = 'pay_complete.jade'

    def get(self, request, *args, **kwargs):
        yeepay = third_pay.YeePay()
        result = yeepay.pay_callback(request)

        if result['ret_code']:
            msg = u"充值失败"
            amount = "None"
        else:
            msg = u"充值成功"
            amount = result['amount']
        return self.render_to_response({
            'result': msg,
            'amount': amount
        })

class BindPayQueryView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        pay = third_pay.KuaiPay()
        result = pay.query_bind(request)
        return Response(result)

class BindPayDelView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        pay = third_pay.KuaiPay()
        result = pay.delete_bind(request)
        return Response(result)

class BindPayView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        pay = third_pay.KuaiPay()
        result = pay.pre_pay(request)

        return Response(result)


class KuaiShortPayCallbackView(View):
    """
    快付TR3应答API
    """
    def post(self, request):
        pay = third_pay.KuaiShortPay()
        logger.debug('kuai_pay_tr3 request body: %s' % request.body)
        pm = pay.handle_pay_result(request.body.strip())
        result = pay.pay_callback(pm['user_id'],
                                  pm['amount'],
                                  pm['ret_code'],
                                  pm['message'],
                                  pm['order_id'],
                                  pm['ref_number'],
                                  pm['res_content'],
                                  pm['signature'],
                                  request)

        return HttpResponse(result, content_type='text/xml')


class BindPayDynNumView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        pay = third_pay.KuaiPay()
        result = pay.dynnum_bind_pay(request)
        return Response(result)


class BankCardAddView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        result = third_pay.add_bank_card(request)

        if result.get('ret_code') == 0:
            try:
                CoopRegister(request).process_for_binding_card(request.user)
            except:
                logger.exception('bind_card_callback_failed for %s' % str(request.user))

        return Response(result)


class BankCardListView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        result = third_pay.list_bank_card(request)
        return Response(result)


class BankCardDelView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        result = third_pay.del_bank_card(request)
        return Response(result)


class BankListAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        result = third_pay.list_bank(request)
        return Response(result)


class FEEAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        amount = request.DATA.get("amount", "")
        bank_id = request.DATA.get("bank_id", "")
        card_id = request.DATA.get("card_id", "")
        device = rest_utils.split_ua(request)
        device_type = rest_utils.decide_device(device['device_type'])
        try:
            app_version = device['app_version']
        except KeyError:
            app_version = ''

        if not amount:
            return Response({"ret_code": 30131, "message": u"请输入金额"})

        if device_type == 'pc':
            if not card_id:
                return Response({"ret_code": 30141, "message": u"银行卡选择错误"})
        else:
            if not bank_id:
                if device_type == 'ios' or device_type == 'android':
                    if app_version and app_version < "2.6.3":
                        pass
                    else:
                        return Response({"ret_code": 30137, "message": u"银行卡选择错误"})

        try:
            float(amount)
        except:
            return Response({"ret_code": 30132, 'message': u'金额格式错误'})
        if amount <= 0:
            return Response({"ret_code": 30131, "message": u"请输入金额"})

        amount = util.fmt_two_amount(amount)
        # 计算提现费用 手续费 + 资金管理费
        user = request.user
        margin = user.margin.margin  # 账户余额
        uninvested = user.margin.uninvested  # 充值未投资金额

        if amount > margin:
            return Response({"ret_code": 30139, "message": u"提现金额超出账户可用余额"})

        # 获取费率配置
        fee_misc = WithdrawFee()
        fee_config = fee_misc.get_withdraw_fee_config()

        # 检测提现最大最小金额
        max_amount = fee_config.get('max_amount')
        min_amount = fee_config.get('min_amount')
        if amount > max_amount:
            return Response({"ret_code": 30133, 'message': u'提现金额超出最大提现限额'})
        if amount < min_amount:
            if margin > min_amount:
                return Response({"ret_code": 30134, 'message': u'提现金额必须大于{}元'.format(min_amount)})
            else:
                if amount != margin:
                    return Response({"ret_code": 30138, 'message': u'账户余额小于{}元时须一次性提完'.format(min_amount)})

        # 检测银行的单笔最大提现限额,如民生银行
        withdraw_limit = ''
        if bank_id and card_id:
            bank = Bank.objects.filter(code=bank_id.upper()).first()
            try:
                card = Card.objects.get(pk=card_id)
            except Card.DoesNotExist:
                card = None
            if bank.id != card.bank.id:
                return Response({"ret_code": 30140, 'message': u'银行选择错误'})
            else:
                if card:
                    withdraw_limit = card.bank.withdraw_limit
                elif bank and bank.withdraw_limit:
                    withdraw_limit = bank.withdraw_limit
        elif card_id and not bank_id:
            try:
                card = Card.objects.get(pk=card_id)
                withdraw_limit = card.bank.withdraw_limit
            except Card.DoesNotExist:
                pass
        elif bank_id and not card_id:
            bank = Bank.objects.filter(code=bank_id.upper()).first()
            if bank and bank.withdraw_limit:
                withdraw_limit = bank.withdraw_limit

        if withdraw_limit:
            bank_limit = util.handle_withdraw_limit(withdraw_limit)
            bank_max_amount = bank_limit.get('bank_max_amount', 0)
            if bank_max_amount:
                if amount > bank_max_amount:
                    return Response({"ret_code": 30135, 'message': u'提现金额超出银行最大提现限额'})

        # 获取计算后的费率
        fee, management_fee, management_amount = fee_misc.get_withdraw_fee(user, amount, margin, uninvested)

        actual_amount = amount - fee - management_fee  # 实际到账金额
        if actual_amount <= 0:
            return Response({"ret_code": 30136, "message": u'余额不足，提现失败'})

        if device_type == 'ios' or device_type == 'android':
            if app_version and app_version < "2.6.3":
                fee = fee + management_fee

        return Response({
            "ret_code": 0,
            "actual_amount": actual_amount,
            "fee": fee,  # 手续费
            "management_fee": management_fee,  # 管理费
            "management_amount": management_amount,  # 计算管理费的金额
        })


class TradeRecordAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        rs = trade_record.detect(request)
        return Response(rs)


class WithdrawAPIView(DecryptParmsAPIView):
    permission_classes = (IsAuthenticated, )

    @require_trade_pwd
    def post(self, request):
        result = third_pay.withdraw(request)

        # 短信通知添加用户名
        user = request.user
        name = user.wanglibaouserprofile.name or u'用户'
        if not result['ret_code']:
            withdraw_submit_ok.apply_async(kwargs={
                "user_id": user.id,
                "user_name": name,
                "phone": request.user.wanglibaouserprofile.phone,
                "amount": result['amount'],
                "bank_name": result['bank_name']
            })
        return Response(result)

class BindCardQueryView(APIView):
    """ 查询用户绑定卡号列表接口 """
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        result = third_pay.card_bind_list(request)
        return Response(result)


class UnbindCardView(APIView):
    """ 解绑卡接口 """
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        result = third_pay.card_unbind(request)
        return Response(result)

class BindPayDepositView(DecryptParmsAPIView):
    """ 获取验证码或快捷支付 """
    permission_classes = (IsAuthenticated, )

    @require_trade_pwd
    def post(self, request):
        result = third_pay.bind_pay_deposit(request)

        return Response(result)

class BindPayDynnumNewView(DecryptParmsAPIView):
    """ 确认支付 """
    permission_classes = (IsAuthenticated, )

    @require_trade_pwd
    def post(self, request):
        result = third_pay.bind_pay_dynnum(request)

        return Response(result)

class BankCardDelNewView(APIView):
    """ 删除银行卡新接口，需要解绑三个渠道"""
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        result = third_pay.del_bank_card_new(request)
        return Response(result)

class BankListNewAPIView(APIView):
    """ 可充值银行列表 """
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        result = third_pay.list_bank_new(request)
        return Response(result)

class YeeShortPayCallbackView(APIView):
    """ 易宝回调 """
    permission_classes = ()

    def post(self, request):
        request.GET = request.DATA
        result = third_pay.yee_callback(request)
        return Response(result)

class UnbindCardTemplateView(TemplateView):
    """
    同卡进出，提供给客服的解绑页面
    """
    template_name = 'unbind_card.jade'

    def get_context_data(self, **kwargs):
        phone = self.request.GET.get('phone')
        if not phone:
            return {'phone': None}

        #解绑
        profile = WanglibaoUserProfile.objects.get(phone=phone)
        the_one_card = TheOneCard(profile.user)
        if self.request.GET.get('unbind'):
            the_one_card.unbind()

        #返回用户名，电话，身份证，发卡行，卡号，有图像返回图像
        try:
            card = the_one_card.get()
            card_number = card.no
            bank_name = card.bank.name
        except:
            card_number = None
            bank_name = None
        try:
            avatar_url = IdVerification.objects.filter(id_number=profile.id_number).first().id_photo.url
        except:
            avatar_url = None

        print avatar_url
        return {'name': profile.name, 'phone': profile.phone, 'social_id': profile.id_number,
                'bank_name': bank_name, 'card_number': card_number, 'avatar_url': avatar_url}




