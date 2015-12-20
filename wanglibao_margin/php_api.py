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
from wanglibao_margin.tasks import buy_month_product, month_product_buy_fail, month_product_check, month_product_cancel, \
    month_product_refund
from wanglibao_margin.php_utils import get_user_info, get_margin_info, PhpMarginKeeper, set_cookie, get_unread_msgs
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

        user_id = request.POST.get('userId')
        token = request.POST.get('token')

        if user_id and token:
            month_product_buy_fail.apply_async(
                    kwargs={'user_id': user_id, 'token': token})
            return HttpResponse(renderers.JSONRenderer().render({'status': '1'}, 'application/json'))
        else:
            return HttpResponse(renderers.JSONRenderer().render(
                {'status': '0', 'msg': 'args error!'}, 'application/json'))


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

        product_id = request.POST.get('productId')

        if product_id:

            month_product_check.apply_async(
                kwargs={'product_id': product_id})

            return HttpResponse(renderers.JSONRenderer().render({'status': '1'}, 'application/json'))

        else:
            return HttpResponse(renderers.JSONRenderer().render(
                {'status': '0', 'msg': 'args error!'}, 'application/json'))


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

        tokens = request.POST.get('tokens')
        tokens = tokens.split('|')

        if tokens:
            month_product_cancel.apply_async(
                kwargs={'tokens': tokens})

            return HttpResponse(renderers.JSONRenderer().render({'status': '1'}, 'application/json'))

        else:
            return HttpResponse(renderers.JSONRenderer().render(
                {'status': '0', 'msg': 'args error!'}, 'application/json'))


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

        args = request.POST.get('args')
        if args:
            month_product_refund.apply_async(
                kwargs={'args': args})

            return HttpResponse(renderers.JSONRenderer().render({'status': '1'}, 'application/json'))

        else:
            return HttpResponse(renderers.JSONRenderer().render(
                {'status': '0', 'msg': 'args error!'}, 'application/json'))


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

