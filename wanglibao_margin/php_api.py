#!/usr/bin/env python
# encoding:utf-8
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import renderers
from rest_framework.views import APIView

from wanglibao_account.auth_backends import User
from wanglibao_margin.models import AssignmentOfClaims, MonthProduct
from wanglibao_margin.php_utils import get_user_info, get_margin_info, PhpMarginKeeper
from wanglibao_account import message as inside_message
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
        if user_ids:
            ids = user_ids.split(',')
            ids_list = [int(uid) for uid in ids]
            users = User.objects.filter(pk__in=ids_list)

            ret_str = ''
            for user in users:
                profile = WanglibaoUserProfile.objects.get(user=user)
                ret_str += '{}:{},'.format(user.pk, profile.phone)
            user_info.update(
                status=True,
                user_list=ret_str
            )

        return HttpResponse(renderers.JSONRenderer().render(user_info, 'application/json'))


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

        margin = get_margin_info(request, user_id)

        return HttpResponse(renderers.JSONRenderer().render(margin, 'application/json'))


class SendInsideMessage(APIView):
    """
    author: Zhoudong
    http请求方式: POST  发送站内信。
    http://xxxxxx.com/php/send_message/
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):
        user_id = self.request.POST.get('userId')
        # useless argument.
        # msg_type = self.request.POST.get('msgType')
        title = self.request.POST.get('title')
        content = self.request.POST.get('content')

        try:
            inside_message.send_one.apply_async(kwargs={
                "user_id": user_id,
                "title": title,
                "content": content,
                "mtype": "activity"
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
            user = User.objects.get(id=user_id)
            if trade_password == user.wanglibaouserprofile.trade_pwd:
                ret = {'status': 1, 'message': 'Succeed'}
            else:
                ret = {'status': 0, 'message': 'password error!'}
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

        # 当扣款成功时 , 请后续执行记录 " 全民淘金 "
        # TODO

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
    http://xxxxxx.com/php/yuelibao/check/
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        ret = dict()

        tokens = request.POST.get('tokens')

        try:
            month_products = MonthProduct.objects.filter(token__in=tokens)
            for product in month_products:
                user = product.user
                product_id = product.product_id
                buyer_keeper = PhpMarginKeeper(user, product_id)
                buyer_keeper.settle(product.amount, description='')
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
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        msg_list = list()
        ret = dict()

        args = request.POST.get('args')
        # args = [{'refundId': 1, 'userId': 2, 'productId': 3, 'principal': 4, 'interest': 5,
        #          'increase': 6, 'amount': 4+5+6, 'tradeType': 0, 'remark': 'string', 'plusInterest': '10%'}
        #         {'refundId': 1, 'userId': 2, 'productId': 3, 'principal': 4, 'interest': 5,
        #          'increase': 6, 'amount': 4+5+6, 'tradeType': 0, 'remark': 'string'}...]

        try:
            for arg in eval(args):
                user = User.objects.get(pk=arg['userId'])
                # product = AssignmentOfClaims.objects.get(pk=arg['productId']) if arg['tradeType'] \
                #     else MonthProduct.objects.get(pk=arg['productId'])
                product_id = arg['productId']
                trade_type = u'债转' if arg['tradeType'] else u'投资'
                description = '{}的还款, 类型是{}, 描述是{}'.format(arg['productId'], trade_type, arg['remark'])

                buyer_keeper = PhpMarginKeeper(user, product_id)
                # 字段需要更新. 添加利息.
                buyer_keeper.amortize(arg['principal'], arg['interest'], 0, arg['increase'], description)

                msg_list.append({'refundId': arg['refundId'], 'plusInterest': arg['plusInterest'], 'status': 1})

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
