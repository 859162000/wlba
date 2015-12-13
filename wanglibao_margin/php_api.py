#!/usr/bin/env python
# encoding:utf-8
import datetime
from django.contrib import auth
from django.db import transaction
from django.http.response import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import renderers
from rest_framework.views import APIView

from wanglibao_account.auth_backends import User
from wanglibao_margin.models import AssignmentOfClaims, MonthProduct
from wanglibao_margin.php_utils import get_user_info, get_margin_info, PhpMarginKeeper, set_cookie, calc_php_commission
from wanglibao_account import message as inside_message
from wanglibao_profile.backends import trade_pwd_check
from wanglibao_profile.models import WanglibaoUserProfile


class GetUserInfo(APIView):
    """
    author: Zhoudong
    http请求方式: GET  根据对应session为php获取到需要的用户信息。
    http://xxxxxx.com/php/get_user/?session_id=xilfttertn1c7581eykflhlvrm6s4peo  # 或者 user_ids=111,222,333
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):
        session_id = self.request.REQUEST.get('session_id')
        user_ids = self.request.REQUEST.get('user_ids', None)

        user_info = dict()
        if session_id and not user_ids:
            user_info = get_user_info(request, session_id)
        elif user_ids:
            ids = user_ids.split(',')
            ids_list = [int(uid) for uid in ids]
            users = User.objects.filter(pk__in=ids_list)

            ret_list = list()
            for user in users:
                user_dic = dict()
                profile = WanglibaoUserProfile.objects.get(user=user)
                user_dic.update(user_id=user.pk, mobile=profile.phone, id_number=profile.id_number)
                ret_list.append(user_dic)

            user_info.update(
                status=1,
                user_list=ret_list
            )
        else:
            user_info.update(
                status=0,
            )

        return HttpResponse(renderers.JSONRenderer().render(user_info, 'application/json'))


def logout_with_cookie(request, next_page='/'):
    """
    logout for php, clear session_bak cookie.
    :param request:
    :param next_page:
    :return:
    """
    auth.logout(request)
    # 退出的时候设置时间就清除cookie
    response = HttpResponseRedirect(next_page)
    set_cookie(response, 'session_bak', None, -100)

    return response


class GetMarginInfo(APIView):
    """
    author: Zhoudong
    http请求方式: GET  根据用户ID 得到用户可用余额。
    http://xxxxxx.com/php/margin/?user_id=11111
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):
        user_id = self.request.REQUEST.get('userId')

        margin = get_margin_info(user_id)

        return HttpResponse(renderers.JSONRenderer().render(margin, 'application/json'))


class SendInsideMessage(APIView):
    """
    author: Zhoudong
    http请求方式: POST  发送站内信。
    http://xxxxxx.com/php/send_message/inside/
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):
        user_id = self.request.POST.get('userId')
        # useless argument.
        msg_type = self.request.POST.get('msgType')
        title = self.request.POST.get('title')
        content = self.request.POST.get('content')

        try:
            inside_message.send_one.apply_async(kwargs={
                "user_id": user_id,
                "title": title,
                "content": content,
                "mtype": msg_type
            })
            ret = {'status': 1, 'message': 'Succeed'}
        except Exception, e:
            ret = {'status': 0, 'message': e}

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class SendMessages(APIView):
    """
    author: Zhoudong
    http请求方式: POST  短信。
    http://xxxxxx.com/php/send_messages/
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):
        phones = self.request.POST.get('phones')
        messages = self.request.POST.get('messages')
        ext = request.POST.get('ext', False)

        phones = phones.split('|')
        messages = messages.split('|')

        try:
            from wanglibao_sms.tasks import send_messages
            if not ext:
                send_messages.apply_async(kwargs={
                    'phones': phones,
                    'messages': messages,
                })
            else:
                send_messages.apply_async(kwargs={
                    'phones': phones,
                    'messages': messages,
                    'ext': 666,  # 营销类短信发送必须增加ext参数,值为666
                })
            ret = {'status': 1, 'message': 'Succeed'}
        except Exception, e:
            ret = {'status': 0, 'message': e}

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class CheckTradePassword(APIView):
    """
    author: Zhoudong
    http请求方式: POST  检查交易密码。
    http://xxxxxx.com/php/trade_password/
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def post(self, request):
        user_id = self.request.POST.get('userId')
        trade_password = self.request.POST.get('pwd')

        try:
            ret = trade_pwd_check(user_id, trade_password)
        except Exception, e:
            ret = {'status': 0, 'message': str(e)}

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class YueLiBaoBuy(APIView):
    """
    author: Zhoudong
    http请求方式: POST  保存PHP的月利宝流水, 处理扣款, 加入冻结资金
    http://xxxxxx.com/php/yuelibao/buy/
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        ret = dict()

        trade_id = request.POST.get('tradeId')
        user_id = request.POST.get('userId')
        product_id = request.POST.get('productId')
        token = request.POST.get('token')
        amount = request.POST.get('amount')
        amount_source = request.POST.get('sourceAmount')
        red_packet = request.POST.get('redPacketAmount')
        red_packet_type = request.POST.get('isRedPacket')

        try:
            user = User.objects.get(pk=user_id)
            assignment, status = MonthProduct.objects.get_or_create(
                user=user,
                product_id=product_id,
                trade_id=trade_id,
                token=token,
                amount=amount,
                amount_source=amount_source,
                red_packet=red_packet,
                red_packet_type=red_packet_type,
            )
            # 状态成功, 对买家扣款, 加入冻结资金
            if status:
                try:
                    buyer_keeper = PhpMarginKeeper(user, product_id)
                    buyer_keeper.freeze(amount, description='')
                    assignment.status = True
                    assignment.save()
                    ret.update(status=1,
                               msg='success')
                except Exception, e:
                    ret.update(status=1,
                               msg=str(e))
            else:
                ret.update(status=1,
                           msg='already saved!')
        except Exception, e:
            ret.update(status=0,
                       msg=str(e))
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class YueLiBaoCheck(APIView):
    """
    author: Zhoudong
    http请求方式: POST  满标审核完毕, 减去冻结资金
    http://xxxxxx.com/php/yue/check/
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        ret = dict()

        product_id = request.POST.get('productId')

        try:
            with transaction.atomic(savepoint=True):
                month_products = MonthProduct.objects.filter(product_id=product_id)
                print month_products
                for product in month_products:
                    # 已支付, 直接返回成功
                    if not product.pay_status:
                        user = product.user
                        product_id = product.product_id
                        buyer_keeper = PhpMarginKeeper(user, product_id)
                        trace = buyer_keeper.settle(product.amount, description='')
                        if trace:
                            product.pay_status = True
                            product.save()
<<<<<<< HEAD

                # 进行全民淘金数据写入
                calc_php_commission(product_id)

=======
>>>>>>> update user info in redis
                ret.update(status=1,
                           msg='success')
        except Exception, e:
            ret.update(status=0,
                       msg=str(e))
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class YueLiBaoCommission(APIView):
    """
    author: Zhoudong
    http请求方式: GET  根据用户ID 得到用户可用余额。
    http://xxxxxx.com/php/commission/?product_id=11111
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):
        try:
            product_id = self.request.REQUEST.get('product_id')
            calc_php_commission(product_id)
            ret = {'status': 1, 'msg': 'success'}
        except Exception, e:
            ret = {'status': 0, 'msg': str(e)}

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class YueLiBaoCancel(APIView):
    """
    author: Zhoudong
    http请求方式: POST  流标, 钱原路返回
    http://xxxxxx.com/php/yuelibao/cancel/
    返回数据格式：json 外层 status = 1 API 成功, 里层status = 1 当个订单返回成功.
    :return:
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        msg_list = []
        ret = dict()

        tokens = eval(request.POST.get('tokens'))

        try:
            with transaction.atomic(savepoint=True):
                month_products = MonthProduct.objects.filter(token__in=tokens)
                for product in month_products:
                    user = product.user
                    product_id = product.product_id
                    buyer_keeper = PhpMarginKeeper(user, product_id)
                    record = buyer_keeper.unfreeze(product.amount, description='')
                    status = 1 if record else 0
                    msg_list.append({'token': product.token, 'status': status})

            ret.update(status=1,
                       msg=msg_list)
        except Exception, e:
            ret.update(status=0,
                       msg=str(e))
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class YueLiBaoRefund(APIView):
    """
    author: Zhoudong
    http请求方式: POST  投资到期回款.
    http://xxxxxx.com/php/yuelibao/refund/
    refundId 还款记录ID 月利宝还款计划表id
    userId 用户ID
    productId 产品ID
    principal 本金
    interest 利息
    increase 加息额
    plusInterest 平台加息
    amount 本次还款金额
    tradeType 产品类型 0月利宝 1债转
    remark 备注 [{"refundId":1,"userId":78641,"amount":15,"tradeType":0,"remark":"string"},
                {"refundId":2,"userId":78694,"amount":15,"tradeType":0,"remark":""}]
        # args = [{'refundId': 1, 'userId': 2, 'productId': 4, 'tradeType': 0, 'remark': 'string',
        #          'amount': 1018, 'principal': 1000, 'interest': 10, 'increase': 5, 'plusInterest': 3},
        #         {'refundId': 2, 'userId': 2, 'amount': 4, 'tradeType': 0, 'remark': 'string',
        #          'amount': 1018, 'principal': 1000, 'interest': 10, 'increase': 5, 'plusInterest': 3},
        #         ...]
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        msg_list = list()
        ret = dict()

        args = request.POST.get('args')

        try:
            with transaction.atomic(savepoint=True):
                for arg in eval(args):
                    user = User.objects.get(pk=arg['userId'])

                    buyer_keeper = PhpMarginKeeper(user, arg['refundId'])
                    try:
                        buyer_keeper.amortize(arg['principal'], arg['interest'], 0,
                                              arg['increase'], description=arg['remark'])
                        msg_list.append({'refundId': arg['refundId'], 'status': 1})
                    except Exception, e:
                        print e
                ret.update(status=1,
                           msg=msg_list)
        except Exception, e:
            ret.update(status=0,
                       msg=str(e))
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class AssignmentOfClaimsBuy(APIView):
    """
    author: Zhoudong
    http请求方式: POST  保存PHP的债转流水, 处理扣款,
    http://xxxxxx.com/php/trade_password/
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        ret = dict()

        buyer_id = request.POST.get('buyerId')
        seller_id = request.POST.get('sellerId')
        product_id = request.POST.get('productId')
        buy_order_id = request.POST.get('buyOrderId')
        sell_order_id = request.POST.get('sellOrderId')
        buyer_token = request.POST.get('buyToken')
        seller_token = request.POST.get('sellToken')
        fee = request.POST.get('fee')
        premium_fee = request.POST.get('premiumFee')
        trading_fee = request.POST.get('tradingFee')
        buy_price = request.POST.get('buyPrice')
        sell_price = request.POST.get('sellPrice')
        buy_price_source = request.POST.get('buyPriceSource')
        sell_price_source = request.POST.get('sellPriceSource')

        try:
            buyer = User.objects.get(pk=buyer_id)
            seller = User.objects.get(pk=seller_id)
            assignment, status = AssignmentOfClaims.objects.get_or_create(
                product_id=product_id,
                buyer=buyer,
                seller=seller,
                buyer_order_id=buy_order_id,
                seller_order_id=sell_order_id,
                buyer_token=buyer_token,
                seller_token=seller_token,
                fee=fee,
                premium_fee=premium_fee,
                trading_fee=trading_fee,
                buy_price=buy_price,
                sell_price=sell_price,
                buy_price_source=buy_price_source,
                sell_price_source=sell_price_source
            )
            # 状态成功, 对买家扣款, 卖家回款.
            if status:
                try:
                    with transaction.atomic(savepoint=True):
                        # status == 0 加钱, 其他减钱. 这直接对买家余额减钱, 卖家余额加钱
                        buyer_keeper = PhpMarginKeeper(buyer, )
                        seller_keeper = PhpMarginKeeper(seller, )
                        buyer_keeper.margin_process(buyer, 1, buy_price, description=u'', catalog=u"买债转")
                        seller_keeper.margin_process(seller, 0, sell_price, description=u'', catalog=u"卖债转")

                        # 如果加减钱成功后, 更新债转的表的状态为成功
                        assignment.status = True
                        assignment.save()
                        ret.update(status=1,
                                   msg='success')
                except Exception, e:
                    ret.update(status=0,
                               msg=str(e))
            else:
                ret.update(status=0,
                           msg='save error')
        except Exception, e:
            ret.update(status=0,
                       msg=str(e))
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))
