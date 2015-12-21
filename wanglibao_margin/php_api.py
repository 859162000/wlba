#!/usr/bin/env python
# encoding:utf-8
import datetime
from django.contrib import auth
from django.db import transaction
from django.db.models import Q
from django.http.response import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import renderers
from rest_framework.views import APIView

from wanglibao_account.auth_backends import User
from wanglibao_margin.models import AssignmentOfClaims, MonthProduct, MarginRecord
from wanglibao_margin.tasks import buy_month_product, assignment_buy
from wanglibao_margin.php_utils import get_user_info, get_margin_info, PhpMarginKeeper, set_cookie, get_unread_msgs, \
    calc_php_commission
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
                user_dic.update(user_id=user.pk, mobile=profile.phone,
                                real_name=profile.name, id_number=profile.id_number)
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


class GetUnreadMgsNum(APIView):
    """
    author: Zhoudong
    http请求方式: GET  根据用户ID 得到用户可用余额。
    http://xxxxxx.com/php/margin/?user_id=11111
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def post(self, request):
        user_id = self.request.REQUEST.get('userId')

        ret = get_unread_msgs(user_id)

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class GetUserUnreadMgsNum(APIView):
    """
    author: Zhoudong
    http请求方式: GET  根据用户ID 得到用户可用余额。
    http://xxxxxx.com/php/margin/?user_id=11111
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):
        user_id = self.request.user.pk

        ret = get_unread_msgs(user_id)

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


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
    http://xxxxxx.com/php/yue/buy/
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        trade_id = request.POST.get('tradeId')
        user_id = request.POST.get('userId')
        product_id = request.POST.get('productId')
        token = request.POST.get('token')
        amount = request.POST.get('amount')
        amount_source = request.POST.get('sourceAmount')
        red_packet = request.POST.get('redPacketAmount')
        red_packet_type = request.POST.get('isRedPacket')

        if trade_id and user_id and product_id and token and amount\
                and amount_source and red_packet and red_packet_type:
            try:
                buy_month_product.apply_async(
                    kwargs={'trade_id': trade_id, 'user_id': user_id, 'product_id': product_id,
                            'token': token, 'amount': amount, 'amount_source': amount_source,
                            'red_packet': red_packet, 'red_packet_type': red_packet_type})
            except Exception, e:
                print e

            return HttpResponse(renderers.JSONRenderer().render({'status': '1'}, 'application/json'))
        else:
            return HttpResponse(renderers.JSONRenderer().render(
                {'status': '0', 'msg': 'args error!'}, 'application/json'))


class YueLiBaoBuyFail(APIView):
    """
    author: Zhoudong
    http请求方式: POST  当主站扣款成功, 新平台没接收到, 调用该接口说明购买失败
    http://xxxxxx.com/php/yue/fail/
    :return: status = 1  成功, status = 0 失败 .
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        ret = dict()

        user_id = request.POST.get('userId')
        token = request.POST.get('token')

        user = User.objects.get(pk=user_id)
        product = MonthProduct.objects.filter(token=token).first()

        # if user != request.user:
        #     ret.update(status=0, msg='user authenticate error')
        #     return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))
        if not product:
            ret.update(status=2, msg='success')
            return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))
        if product.cancel_status:
            ret.update(status=1, msg='success')
            return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))

        try:
            with transaction.atomic(savepoint=True):
                product_id = product.product_id
                buyer_keeper = PhpMarginKeeper(user, product_id)
                record = buyer_keeper.yue_cancel(user, product.amount)

                if record:
                    # 状态置为已退款, 这个记录丢弃
                    product.cancel_status = True
                    product.save()

            ret.update(status=1,
                       msg='success')
        except Exception, e:
            ret.update(status=0,
                       msg=str(e))
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class YueLiBaoBuyStatus(APIView):
    """
    author: Zhoudong
    http请求方式: POST
    http://xxxxxx.com/php/yue/status/
    :return: status = 1  成功, status = 0 失败 .
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        ret = dict()

        token = request.POST.get('token')

        product = MonthProduct.objects.filter(token=token).first()

        if not product:
            ret.update(status=-1, msg='trade does not exist!')
        elif product.pay_status:
            ret.update(status=1, msg='trade success!')
        else:
            ret.update(status=0,
                       msg='pay failed!')
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
                month_products = MonthProduct.objects.filter(
                    product_id=product_id, cancel_status=False, pay_status=False)

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

                # 进行全民淘金数据写入
                calc_php_commission(product_id)

                ret.update(status=1,
                           msg='success')
        except Exception, e:
            ret.update(status=0,
                       msg=str(e))
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class YueLiBaoCancel(APIView):
    """
    author: Zhoudong
    http请求方式: POST  流标, 钱原路返回
    http://xxxxxx.com/php/yue/cancel/
    返回数据格式：json 外层 status = 1 API 成功, 里层status = 1 当个订单返回成功.
    :return:
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        msg_list = []
        ret = dict()

        tokens = request.POST.get('tokens')
        tokens = tokens.split('|')

        try:
            with transaction.atomic(savepoint=True):
                month_products = MonthProduct.objects.filter(token__in=tokens)
                for product in month_products:
                    user = product.user
                    product_id = product.product_id
                    buyer_keeper = PhpMarginKeeper(user, product_id)
                    record = buyer_keeper.unfreeze(product.amount, description='')

                    # 状态置为已退款, 这个记录丢弃
                    product.cancel_status = True
                    product.save()

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
    http://xxxxxx.com/php/yue/refund/
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

                    margin_record = MarginRecord.objects.filter(
                        # (Q(catalog=u'月礼包本金入账') | Q(catalog=u'债转本金入账')) &
                        (Q(catalog=u'\u6708\u5229\u5b9d\u672c\u91d1\u5165\u8d26') |
                         Q(catalog=u'\u503a\u8f6c\u672c\u91d1\u5165\u8d26')) &
                        Q(order_id=arg['refundId']) & Q(user=user)
                    ).first()

                    if margin_record:
                        msg_list.append({'refundId': arg['refundId'], 'status': 1})

                    else:
                        buyer_keeper = PhpMarginKeeper(user, arg['refundId'])

                        try:
                            buyer_keeper.php_amortize_detail(
                                arg['tradeType'], arg['principal'], arg['interest'], 0, arg['increase'],
                                arg['plusInterest'], arg['refundId']
                            )
                            msg_list.append({'refundId': arg['refundId'], 'status': 1})

                        except Exception, e:
                            print e
                            ret.update(status=0,
                                       msg=str(e))
                            return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))

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
    http://xxxxxx.com/php/assignment/buy/
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

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

        if buyer_id and seller_id and product_id and buy_order_id and sell_order_id and buyer_token and seller_token\
                and fee and premium_fee and trading_fee and buy_price and sell_price and buy_price_source \
                and sell_price_source:

            assignment_buy.apply_async(
                kwargs={'buyer_id': buyer_id, 'seller_id': seller_id, 'product_id': product_id,
                        'buy_order_id': buy_order_id, 'sell_order_id': sell_order_id, 'buyer_token': buyer_token,
                        'seller_token': seller_token, 'fee': fee, 'premium_fee': premium_fee,
                        'trading_fee': trading_fee, 'buy_price': buy_price, 'sell_price': sell_price,
                        'buy_price_source': buy_price_source, 'sell_price_source': sell_price_source})

            return HttpResponse(renderers.JSONRenderer().render({'status': '1'}, 'application/json'))

        else:
            return HttpResponse(renderers.JSONRenderer().render(
                {'status': '0', 'msg': 'args error!'}, 'application/json'))


class AssignmentBuyStatus(APIView):
    """
    author: Zhoudong
    http请求方式: POST
    http://xxxxxx.com/php/yue/status/
    :return: status = 1  成功, status = 0 失败 .
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        ret = dict()

        buyer_token = request.POST.get('buyToken')
        seller_token = request.POST.get('sellToken')

        assignment = AssignmentOfClaims.objects.filter(buyer_token=buyer_token, seller_token=seller_token).first()

        if not assignment:
            ret.update(status=-1, msg='trade does not exist!')
        elif assignment.status:
            ret.update(status=1, msg='trade success!')
        else:
            ret.update(status=0,
                       msg='assignment pay failed!')
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class AssignmentBuyFail(APIView):
    """
    author: Zhoudong
    http请求方式: POST  当主站扣款成功, 新平台没接收到, 调用该接口说明购买失败
    http://xxxxxx.com/php/assignment/fail/
    :return: status = 1  成功, status = 0 失败 .
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        ret = dict()

        buyer_id = request.POST.get('buyerId')
        seller_id = request.POST.get('sellerId')
        buy_token = request.POST.get('buyToken')
        sell_token = request.POST.get('sellToken')

        assignment = AssignmentOfClaims.objects.filter(
            buyer_id=buyer_id, seller_id=seller_id, buyer_token=buy_token, seller_token=sell_token, status=True).first()

        if not assignment:
            assignment = AssignmentOfClaims.objects.filter(
                buyer_id=buyer_id, seller_id=seller_id, buyer_token=buy_token, seller_token=sell_token).first()
            if assignment:
                ret.update(status=1, msg='success')
                return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))
            ret.update(status=2, msg='success')
            return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))

        try:
            with transaction.atomic(savepoint=True):

                buyer = assignment.buyer
                seller = assignment.seller
                product_id = assignment.product_id
                buyer_keeper = PhpMarginKeeper(buyer, product_id)
                seller_keeper = PhpMarginKeeper(seller, product_id)

                a = buyer_keeper.margin_process(buyer, 0, assignment.buy_price, u'买家债转退款', u'债转购买失败回滚')
                b = seller_keeper.margin_process(seller, 1, assignment.sell_price, u'卖家债转退款', u'债转购买失败回滚')
                if a and b:
                    assignment.status = False
                    assignment.save()

                ret.update(status=1,
                           msg='success')
        except Exception, e:
            ret.update(status=0,
                       msg=str(e))
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))
