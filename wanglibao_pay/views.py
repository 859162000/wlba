#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
import socket
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect
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
from wanglibao_margin.exceptions import MarginLack
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_pay.models import Bank, Card, PayResult, PayInfo
from wanglibao_pay.huifu_pay import HuifuPay, SignException
from wanglibao_pay import third_pay, trade_record
from wanglibao_p2p.models import P2PRecord
import decimal
from wanglibao_pay.serializers import CardSerializer
from wanglibao_pay.util import get_client_ip
from wanglibao_pay import util
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_sms import messages
from wanglibao_sms.tasks import send_messages
from wanglibao_account import message as inside_message
from wanglibao.const import ErrorNumber
from wanglibao_sms.utils import validate_validation_code
from django.conf import settings
from wanglibao_announcement.utility import AnnouncementAccounts

logger = logging.getLogger(__name__)
TWO_PLACES = decimal.Decimal(10) ** -2


class BankListView(TemplateView):
    template_name = 'pay_banks.jade'

    def get_context_data(self, **kwargs):
        context = super(BankListView, self).get_context_data(**kwargs)

        default_bank = Bank.get_deposit_banks().filter(
            name=self.request.user.wanglibaouserprofile.deposit_default_bank_name).first()

        context.update({
            'default_bank': default_bank,
            'banks': Bank.get_deposit_banks()[:12],
            'announcements': AnnouncementAccounts
        })
        return context


class PayView(TemplateView):
    template_name = 'pay_jump.jade'

    def post(self, request):
        if not request.user.wanglibaouserprofile.id_is_valid:
            return self.render_to_response({
                'message': u'请先进行实名认证'
            })
        form = dict()
        message = ''
        try:
            amount_str = request.POST.get('amount', '')
            amount = decimal.Decimal(amount_str). \
                quantize(TWO_PLACES, context=decimal.Context(traps=[decimal.Inexact]))
            amount_str = str(amount)
            if amount <= 0:
                # todo handler the raise
                raise decimal.DecimalException()

            gate_id = request.POST.get('gate_id', '')
            bank = Bank.objects.get(gate_id=gate_id)

            # Store this as the default bank
            request.user.wanglibaouserprofile.deposit_default_bank_name = bank.name
            request.user.wanglibaouserprofile.save()

            pay_info = PayInfo()
            pay_info.amount = amount
            pay_info.total_amount = amount
            pay_info.type = PayInfo.DEPOSIT
            pay_info.status = PayInfo.INITIAL
            pay_info.user = request.user
            pay_info.bank = bank
            pay_info.channel = "huifu"
            pay_info.request_ip = get_client_ip(request)

            order = OrderHelper.place_order(request.user, Order.PAY_ORDER, pay_info.status,
                                            pay_info=model_to_dict(pay_info))
            pay_info.order = order
            pay_info.save()

            post = {
                'OrdId': pay_info.pk,
                'GateId': gate_id,
                'OrdAmt': amount_str
            }

            pay = HuifuPay()
            form = pay.pay(post)
            pay_info.request = str(form)
            pay_info.status = PayInfo.PROCESSING
            pay_info.save()
            OrderHelper.update_order(order, request.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
        except decimal.DecimalException:
            message = u'金额格式错误'
        except Bank.DoesNotExist:
            message = u'请选择有效的银行'
        except (socket.error, SignException) as e:
            message = PayResult.RETRY
            pay_info.status = PayInfo.FAIL
            pay_info.error_message = str(e)
            pay_info.save()
            OrderHelper.update_order(order, request.user, pay_info=model_to_dict(pay_info), status=pay_info.status)
            logger.fatal('sign error! order id: ' + str(pay_info.pk) + ' ' + str(e))

        context = {
            'message': message,
            'form': form
        }
        return self.render_to_response(context)

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


class WithdrawView(TemplateView):
    template_name = 'withdraw.jade'

    def get_context_data(self, **kwargs):
        cards = Card.objects.filter(user=self.request.user).order_by("-is_default").select_related()
        banks = Bank.get_withdraw_banks()
        return {
            'cards': cards,
            'banks': banks,
            'user_profile': self.request.user.wanglibaouserprofile,
            'margin': self.request.user.margin.margin,
            'fee': HuifuPay.FEE,
            'announcements': AnnouncementAccounts
        }


class WithdrawCompleteView(TemplateView):
    template_name = 'withdraw_complete.jade'

    @method_decorator(transaction.atomic)
    def post(self, request, *args, **kwargs):
        if not request.user.wanglibaouserprofile.id_is_valid:
            return self.render_to_response({
                'result': u'请先进行实名认证'
            })
        phone = request.user.wanglibaouserprofile.phone
        code = request.POST.get('validate_code', '')
        status, message = validate_validation_code(phone, code)
        if status != 200:
            return self.render_to_response({
                'result': u'验证码输入错误'
            })

        result = PayResult.WITHDRAW_SUCCESS
        try:

            amount_str = request.POST.get('amount', '')
            amount = decimal.Decimal(amount_str). \
                quantize(TWO_PLACES, context=decimal.Context(traps=[decimal.Inexact]))
            margin = self.request.user.margin.margin
            if amount > 50000 or amount <= 0:
                raise decimal.DecimalException
            if amount < 50:
                if amount != margin:
                    raise decimal.DecimalException

            fee = (amount * HuifuPay.FEE).quantize(TWO_PLACES)
            actual_amount = amount - fee

            card_id = request.POST.get('card_id', '')
            card = Card.objects.get(pk=card_id)

            pay_info = PayInfo()
            pay_info.amount = actual_amount
            pay_info.fee = fee
            pay_info.total_amount = amount
            pay_info.type = PayInfo.WITHDRAW
            pay_info.user = request.user
            pay_info.card_no = card.no
            pay_info.account_name = request.user.wanglibaouserprofile.name
            pay_info.bank = card.bank
            pay_info.request_ip = get_client_ip(request)
            pay_info.status = PayInfo.ACCEPTED

            order = OrderHelper.place_order(request.user, Order.WITHDRAW_ORDER, pay_info.status,
                                            pay_info=model_to_dict(pay_info))

            pay_info.order = order
            keeper = MarginKeeper(request.user, pay_info.order.pk)
            margin_record = keeper.withdraw_pre_freeze(amount)
            pay_info.margin_record = margin_record

            pay_info.save()

            send_messages.apply_async(kwargs={
                'phones': [request.user.wanglibaouserprofile.phone],
                'messages': [messages.withdraw_submitted(amount, timezone.now())]
            })
            title, content = messages.msg_withdraw(timezone.now(), amount)
            inside_message.send_one.apply_async(kwargs={
                "user_id": request.user.id,
                "title": title,
                "content": content,
                "mtype": "withdraw"
            })
        except decimal.DecimalException:
            result = u'提款金额在0～50000之间'
        except Card.DoesNotExist:
            result = u'请选择有效的银行卡'
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

        exist_cards = Card.objects.filter(no=card.no, bank__id=bank_id, user__id=card.user.id)
        exist_cards1 = Card.objects.filter(user=card.user, no__startswith=card.no[:6], no__endswith=card.no[-4:]).first()
        if exist_cards or exist_cards1:
            return Response({
                                "message": u"该银行卡已经存在",
                                'error_number': ErrorNumber.duplicate
                            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            card.bank = Bank.objects.get(pk=bank_id)
        except:
            return Response({
                                "message": u"没有找到该银行",
                                'error_number': ErrorNumber.not_find
                            }, status=status.HTTP_400_BAD_REQUEST)

        card.save()

        return Response({
            'id': card.pk,
            'no': card.no,
            'bank_name': card.bank.name
        })


    def destroy(self, request, pk=None):
        card_id = request.DATA.get('card_id', '')
        card = Card.objects.filter(id=card_id)
        if card:
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
        payinfos = PayInfo.objects.filter(uuid__in=uuids, type='W')

        # These are the uuids exists in db for real
        uuids_param = ",".join([payinfo.uuid for payinfo in payinfos])

        if action == 'preview' or action is None:
            return self.render_to_response(
                {
                    'payinfos': payinfos,
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

                    marginKeeper = MarginKeeper(payinfo.user)
                    marginKeeper.withdraw_ack(payinfo.amount)

                    payinfo.status = PayInfo.SUCCESS
                    payinfo.confirm_time = timezone.now()
                    payinfo.save()
                    # 发站内信
                    title, content = messages.msg_withdraw_success(timezone.now(), payinfo.amount)
                    inside_message.send_one.apply_async(kwargs={
                        "user_id": payinfo.user_id,
                        "title": title,
                        "content": content,
                        "mtype": "withdraw"
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
        marginKeeper.withdraw_rollback(payinfo.amount, error_message)
        payinfo.status = PayInfo.FAIL
        payinfo.error_message = error_message
        payinfo.confirm_time = None
        payinfo.save()

        send_messages.apply_async(kwargs={
            "phones": [payinfo.user.wanglibaouserprofile.phone],
            "messages": [messages.withdraw_failed(error_message)]
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
class YeePayAppPayView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        yeepay = third_pay.YeePay()
        result = yeepay.app_pay(request)
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
        gate_id = request.DATA.get("gate_id")
        if not gate_id:
            return Response({"ret_code": -1, "message": "gate_id is null"})
        bank = Bank.objects.filter(gate_id=gate_id).first()
        if not bank:
            return Response({"ret_code": -2, "message": "gate_id error"})
        channel_dict = {"huifu":   third_pay.HuifuShortPay,
                        "yeepay":  third_pay.YeePay,
                        "kuaipay": third_pay.KuaiPay}
        bank.channel = 'huifu'
        pay = channel_dict[bank.channel]()
        result = pay.pre_pay(request)
        return Response(result)

class BindPayCallbackView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        pay = third_pay.KuaiPay()
        result = pay.pay_callback(request)
        return Response(result)

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
        amount = request.DATA.get("amount", "").strip()
        if not amount:
            return Response({"ret_code": 30131, "message": "请输入金额"})

        try:
            float(amount)
        except:
            return {"ret_code": 30132, 'message': '金额格式错误'}

        amount = util.fmt_two_amount(amount)
        #计算费率

        return Response({"ret_code": 0, "fee": 0})

class TradeRecordAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        rs = trade_record.detect(request)
        return Response(rs)


class WithdrawAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        result = third_pay.withdraw(request)
        if not result['ret_code']:
            send_messages.apply_async(kwargs={
                'phones': [result['phone']],
                'messages': [messages.withdraw_submitted(result['amount'], timezone.now())]
            })

            title, content = messages.msg_withdraw(timezone.now(), result['amount'])
            inside_message.send_one.apply_async(kwargs={
                "user_id": request.user.id,
                "title": title,
                "content": content,
                "mtype": "withdraw"
            })
        return Response(result)
