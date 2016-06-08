#!/usr/bin/env python
# encoding:utf-8
import logging

from django.contrib import auth
from django.db import transaction
from django.db.models import Q
from django.http.response import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import renderers
from rest_framework.authentication import BasicAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from marketing import tools
from wanglibao import settings
from wanglibao_account.auth_backends import User
from wanglibao_account.cooperation import CoopRegister
from wanglibao_margin.models import AssignmentOfClaims, MonthProduct, MarginRecord
from wanglibao_margin.tasks import buy_month_product, assignment_buy, buy_mall_product
from wanglibao_margin.php_utils import get_user_info, get_margin_info, PhpMarginKeeper, set_cookie, get_unread_msgs, \
    calc_php_commission, php_redpacks, send_redpacks, php_redpack_restore, CsrfExemptSessionAuthentication, \
    get_addresses, get_mall_locked_amount
from wanglibao_account import message as inside_message
from wanglibao_profile.backends import trade_pwd_check
from wanglibao_profile.models import WanglibaoUserProfile

from wanglibao_rest import utils
from wanglibao_rest.common import PHPDecryptParmsAPIView


logger = logging.getLogger('wanglibao_margin')


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
        token = self.request.REQUEST.get('token')
        user_ids = self.request.REQUEST.get('user_ids', None)

        user_info = dict()
        if session_id and not user_ids:
            user_info = get_user_info(request, session_id)
        elif token and not user_ids:
            user_info = get_user_info(request, None, token)
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
    http请求方式: GET  根据用户ID 得到用户可用余额。
    http://xxxxxx.com/php/margin/?user_id=11111
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):

        user_id = self.request.REQUEST.get('userId')
        url = 'https://' + request.get_host() + settings.PHP_UNPAID_PRINCIPLE_BASE
        try:
            if int(self.request.get_host().split(':')[1]) > 7000:
                url = settings.PHP_APP_INDEX_DATA_DEV
        except Exception, e:
            pass

        margin = get_margin_info(user_id, url)

        return HttpResponse(renderers.JSONRenderer().render(margin, 'application/json'))


class GetUnreadMgsNum(APIView):
    """
    http请求方式: GET  根据用户ID 得到用户未读站内信数量。
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
    http请求方式: GET  自己的未读数, 不需要参数。
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):

        user_id = self.request.user.pk
        ret = get_unread_msgs(user_id)

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class GetUserMallAmount(APIView):
    """
    http请求方式: GET  获取到用户在商城的已消费总额。
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):
        user = self.request.user
        ret = get_mall_locked_amount(user)

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class GetUserAddress(APIView):
    """
    http请求方式: GET  给商城的用户地址。
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def get(self, request):

        user_id = self.request.user.pk
        ret = get_addresses(user_id)

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class SendInsideMessage(APIView):
    """
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
            if settings.ENV == settings.ENV_PRODUCTION:
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
            else:
                from wanglibao_sms.send_php import PHPSendSMS
                for phone in phones:
                    PHPSendSMS().send_sms_msg_one(1, phone, 'phone', messages[phones.index(phone)])
                ret = {'status': 1, 'message': 'messages send by PHP.'}
        except Exception, e:
            logger.debug(u'发送短息失败! phones = {}, err = {}'.format(phones, e.message))
            ret = {'status': 0, 'message': e}

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class CheckTradePassword(APIView):
    """
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
            ret = {'status': 0, 'message': e.message}
            logger.debug('CheckTradePassword error with {}!\n'.format(e.message))

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class CheckAppTradePassword(PHPDecryptParmsAPIView):
    """
    http请求方式: POST  检查交易密码。
    http://xxxxxx.com/php/trade_password/
    arg:   password = {"param":"{\\"trade_pwd\\":6}","trade_pwd":"hSna2VQhpYzDmSoZElNlLg=="}
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    def post(self, request):
        trade_password = self.params.get('trade_pwd', "").strip()
        user_id = self.request.POST.get('user_id', "").strip()
        try:
            ret = trade_pwd_check(int(user_id), trade_password)
        except Exception, e:
            ret = {'status': -1, 'message': e.message}
            logger.debug('CheckTradePassword error with {}!\n'.format(e.message))

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class YueLiBaoBuy(APIView):
    """
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
        period = request.POST.get('period', 1)
        # 使用的红包id
        red_packet_id = request.POST.get('RedPacketId', 0)

        try:
            user = User.objects.get(pk=user_id)
            product, status = MonthProduct.objects.get_or_create(
                user=user,
                product_id=product_id,
                trade_id=trade_id,
                token=token,
                amount=amount,
                amount_source=amount_source,
                red_packet=red_packet,
                red_packet_type=red_packet_type,
            )
            device = utils.split_ua(self.request)

            buy_month_product.apply_async(kwargs={'token': token, 'red_packet_id': red_packet_id,
                                                  'amount_source': amount_source, 'user': user_id,
                                                  'device': device, 'period': period}, queue='celery_ylb')

            return HttpResponse(renderers.JSONRenderer().render({'status': '1'}, 'application/json'))

        except Exception, e:
            logger.debug('buy month product failed with {}!\n'.format(e.message))
            return HttpResponse(renderers.JSONRenderer().render(
                {'status': '0', 'msg': 'args error! ' + e.message}, 'application/json'))


class MallProductBuy(APIView):
    """
    http请求方式: POST  保存 商城流水
    http://xxxxxx.com/php/mall/buy/
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        trade_id = request.POST.get('tradeId')
        user_id = request.POST.get('userId')
        product_id = request.POST.get('productId')
        token = request.POST.get('token', None)
        amount = request.POST.get('amount', 0)
        amount_source = request.POST.get('sourceAmount', 0)

        # 给用户的返现金额
        payback_source = request.POST.get('payBackAmount', 0)

        # 红包金额为-1  用于统计已花本金, 还款忽略, 只改状态.
        red_packet = -1
        # 类型, -1 表示未使用红包
        red_packet_type = -1

        try:
            user = User.objects.filter(pk=user_id).first()
            product, status = MonthProduct.objects.get_or_create(
                user=user,
                product_id=product_id,
                trade_id=trade_id,
                token=token,
                amount=amount,
                amount_source=amount_source,
                red_packet=red_packet,
                red_packet_type=red_packet_type,
            )
            device = utils.split_ua(self.request)
            logger.info('going to buy_mall_product !!!')

            buy_mall_product.apply_async(kwargs={'token': token, 'amount_source': amount_source,
                                                 'payback_source': payback_source, 'user': user_id,
                                                 'device_type': device['device_type']})

            return HttpResponse(renderers.JSONRenderer().render({'status': '1'}, 'application/json'))

        except Exception, e:
            logger.debug('buy mall product failed with {}!\n'.format(e.message))
            return HttpResponse(renderers.JSONRenderer().render(
                {'status': '0', 'msg': 'args error! ' + e.message}, 'application/json'))


class YueLiBaoBuyFail(APIView):
    """
    http请求方式: POST  当主站扣款成功(或者未扣款), 新平台没接收到返回也查不到状态, 调用该接口说明购买失败
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

        # 不存在的订单显示成功
        if not product:
            ret.update(status=2, msg='success')
            return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))
        if product.cancel_status:
            ret.update(status=1, msg='already canceled!')
            return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))
        # 未扣款成功的订单, 直接返回成功
        if product.trade_status == 'NEW':
            product.cancel_status = True
            product.save()
            ret.update(status=1, msg='not paid!')
            return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))

        try:
            with transaction.atomic(savepoint=True):
                product_id = product.product_id
                buyer_keeper = PhpMarginKeeper(user, product_id)
                record = buyer_keeper.yue_cancel(user, product.amount_source)

                if record:
                    # 状态置为已退款, 这个记录丢弃
                    product.cancel_status = True
                    product.save()

                    # 增加回退红包接口
                    php_redpack_restore(product.id, product_id, product.amount, user)
                    logger.info('purchase failed and restore red_pack. month_product_id = {},\n'.format(product_id))

            ret.update(status=1,
                       msg='success')
        except Exception, e:
            logger.debug('in YueLiBaoBuyFail, failed with : {}\n'.format(e.message))
            ret.update(status=0,
                       msg=e.message)
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class YueLiBaoBuyStatus(APIView):
    """
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
        elif product.trade_status == 'NEW':
            ret.update(status=1, msg='processing!')
        elif product.trade_status == 'PAID':
            ret.update(status=2, msg='success!')
        else:
            ret.update(status=0,
                       msg='pay failed!')
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class YueLiBaoCheck(APIView):
    """
    http请求方式: POST  满标审核完毕, 减去冻结资金
    http://xxxxxx.com/php/yue/check/
    返回数据格式：json
    :return:
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        logger.info('in YueLiBaoCheck!!!!!!')

        ret = dict()

        product_id = request.POST.get('productId')
        period = int(request.POST.get('period'))

        try:
            with transaction.atomic(savepoint=True):
                month_products = MonthProduct.objects.filter(
                    product_id=product_id, cancel_status=False, trade_status='PAID')

                for product in month_products:
                    if product.red_packet == -1:
                        product.red_packet = 0
                        product.save()
                        continue
                    if product.settle_status:
                        logger.info(u'该条记录已审核: product = {}, 这是重复请求, product_id = {}'.
                                    format(product.id), product_id)
                        continue
                    product.settle_status = True
                    product.save()
                    # 已支付, 直接返回成功
                    user = product.user
                    product_id = product.product_id
                    buyer_keeper = PhpMarginKeeper(user, product_id)
                    buyer_keeper.php_settle(product.amount_source, description=u'月利宝满标审核')

                # 进行全民淘金数据写入
                if period >= 3:
                    calc_php_commission(product_id)
                    logger.info(u'period = {}, 全民淘金数据写入: {}\n'.format(period, product_id))

                ret.update(status=1,
                           msg='success')
        except Exception, e:
            logger.debug(u'月利宝id: {} 满标审核失败: {}\n'.format(product_id, e.message))
            ret.update(status=0,
                       msg=e.message)
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class YueLiBaoCancel(APIView):
    """
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
        logger.info(u'流标 tokens = {}'.format(tokens))

        try:
            with transaction.atomic(savepoint=True):
                month_products = MonthProduct.objects.filter(token__in=tokens)
                for product in month_products:
                    user = product.user
                    product_id = product.product_id
                    buyer_keeper = PhpMarginKeeper(user, product_id)
                    record = buyer_keeper.php_unfreeze(product.amount_source, description=u'月利宝流标')

                    # 状态置为已退款, 这个记录丢弃
                    product.cancel_status = True
                    product.save()
                    logger.info('cancel_status saved as true! month_product_id = {}'.format(product_id))

                    # 增加回退红包接口
                    result = php_redpack_restore(product.id, product_id, product.amount_source, user)
                    logger.info(u'判断是否有红包, month_product_id = {}'.format(product_id))
                    # 用户红包金额退回
                    if result['ret_code'] != -1:
                        logger.info(u'使用过红包. result = {}, result["ret_code"] = {}'.format(result, result['ret_code']))
                        buyer_keeper.redpack_return(result['deduct'],
                                                    description=u"月利宝id=%s流标 红包退回%s元" % (product_id, result['deduct']))

                    status = 1 if record else 0
                    msg_list.append({'token': product.token, 'status': status})

            ret.update(status=1,
                       msg=msg_list)
            logger.info(u'tokens = {}, 流标成功\n'.format(tokens))
        except Exception, e:
            logger.debug(u'tokens = {}, 流标失败: {}\n'.format(tokens, e.message))
            ret.update(status=0,
                       msg=e.message)
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class YueLiBaoRefund(APIView):
    """
    http请求方式: POST  投资到期回款.
    http://xxxxxx.com/php/yue/refund/
    refundId 还款记录ID 月利宝还款计划表id
    userId 用户ID
    productId 产品ID
    principal 本金
    interest 利息
    increase 加息额
    plusInterest 平台加息
    t0Interest t+0 利息
    amount 本次还款金额
    tradeType 产品类型 0月利宝 1债转
    remark 备注
    # args = [{'refundId': 1, 'userId': 2, 'productId': 4, 'tradeType': 0, 'remark': 'string',
    #          'amount': 1018, 'principal': 1000, 'interest': 10, 'increase': 5, 'plusInterest': 3, 'add_interest': 6},
    #         {'refundId': 2, 'userId': 2, 'amount': 4, 'tradeType': 0, 'remark': 'string',
    #          'amount': 1018, 'principal': 1000, 'interest': 10, 'increase': 5, 'plusInterest': 3, 'add_interest': 6},
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
        logger.info('in YueLiBaoRefund, args = '.format(args))
        logger.info('YueLiBaoRefund request data = {}'.format(request.DATA))

        try:
            with transaction.atomic(savepoint=True):
                for arg in eval(args):
                    logger.info('!@#$%^&* arg = {}'.format(arg))
                    user = User.objects.get(pk=arg['userId'])

                    margin_record = MarginRecord.objects.filter(
                        # # (Q(catalog=u'月利宝本金入账') | Q(catalog=u'债转本金入账')) &
                        # (Q(catalog=u'\u6708\u5229\u5b9d\u672c\u91d1\u5165\u8d26') |
                        #  Q(catalog=u'\u503a\u8f6c\u672c\u91d1\u5165\u8d26')) &

                        # u'月利宝本金入账' 和 u'债转本金入账'  ---> u'回款本金'
                        # Q(catalog=u'回款本金') &
                        Q(catalog=u'\u56de\u6b3e\u672c\u91d1') &
                        Q(order_id=arg['refundId']) & Q(user=user)
                    ).first()

                    if margin_record:
                        logger.info('refund_ID = {} has been refunded already!!! '.format(arg['refundId']))
                        msg_list.append({'refundId': arg['refundId'], 'status': 1})

                    else:
                        buyer_keeper = PhpMarginKeeper(user, arg['refundId'])

                        try:
                            buyer_keeper.php_amortize_detail(
                                arg['tradeType'], arg['principal'], arg['interest'], arg['add_interest'],
                                arg['increase'], arg['plusInterest'], arg['refundId']
                            )
                            msg_list.append({'refundId': arg['refundId'], 'status': 1})

                        except Exception, e:
                            ret.update(status=0,
                                       msg=e.message)
                            logger.debug('in YueLiBaoRefund error = {}\n'.format(e.message))
                            return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))

                ret.update(status=1,
                           msg=msg_list)

        except Exception, e:
            ret.update(status=0,
                       msg=e.message)
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class AssignmentOfClaimsBuy(APIView):
    """
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

            assignment_buy.apply_async(
                kwargs={'buyer_token': buyer_token, 'seller_token': seller_token}, queue='celery_ylb')

            return HttpResponse(renderers.JSONRenderer().render({'status': '1'}, 'application/json'))

        except Exception, e:
            return HttpResponse(renderers.JSONRenderer().render(
                {'status': '0', 'msg': 'args error! ' + e.message}, 'application/json'))


class AssignmentBuyStatus(APIView):
    """
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
        elif assignment.trade_status == 'NEW':
            ret.update(status=1, msg='processing!')
        elif assignment.trade_status == 'PAID':
            ret.update(status=2, msg='success!')
        else:
            ret.update(status=0,
                       msg='pay failed!')

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class AssignmentBuyFail(APIView):
    """
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
                       msg=e.message)
        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class GetRedPacks(APIView):
    """
    http请求方式: post
    http://xxxxxx.com/php/redpacks/list/
    period = int()
    :return: status = 1  成功, status = 0 失败 .
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        red_pack_info = dict()
        period = request.POST.get('period', 0)
        uid = request.POST.get('userId', 0)

        if request.user.id:
            uid = request.user.id

        # if self.request.user.pk and int(self.request.user.pk) == int(uid):
        # 去掉登录验证, 方便PHP
        if period and uid:
            device = utils.split_ua(self.request)

            result = php_redpacks(User.objects.get(pk=uid), device['device_type'], period=period)
            redpacks = result['packages'].get('available', [])

            red_pack_info.update(
                status=1,
                redpacks=redpacks
            )
        else:
            red_pack_info.update(
                status=0,
                msg=u'authentic error!'
            )

        return HttpResponse(renderers.JSONRenderer().render(red_pack_info, 'application/json'))


class GetIOSRedPacks(APIView):
    """
    http请求方式: post
    http://xxxxxx.com/php/redpacks/list/
    period = int()
    :return: status = 1  成功, status = 0 失败 .
    """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):

        red_pack_info = dict()
        period = request.POST.get('period', 0)
        uid = request.POST.get('userId', 0)

        if request.user.id:
            uid = request.user.id

        # if self.request.user.pk and int(self.request.user.pk) == int(uid):
        # 去掉登录验证, 方便PHP
        if period and uid:
            device = utils.split_ua(self.request)

            result = php_redpacks(User.objects.get(pk=uid), device['device_type'], period=period)
            redpacks = result['packages'].get('available', [])

            red_pack_info.update(
                status=1,
                redpacks=redpacks
            )
        else:
            red_pack_info.update(
                status=0,
                msg=u'authentic error!'
            )

        return Response(red_pack_info)


class GetAjaxRedPacks(APIView):
    """
    http请求方式: post
    http://xxxxxx.com/php/redpacks/ajax/list/
    period = int()
    :return: status = 1  成功, status = 0 失败 .
    """
    permission_classes = ()
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    @csrf_exempt
    def post(self, request):

        red_pack_info = dict()
        period = request.POST.get('period', 0)
        uid = request.POST.get('userId', 0)

        if request.user.id:
            uid = request.user.id

        # if self.request.user.pk and int(self.request.user.pk) == int(uid):
        # 去掉登录验证, 方便PHP
        if period and uid:
            device = utils.split_ua(self.request)

            result = php_redpacks(User.objects.get(pk=uid), device['device_type'], period=period)
            redpacks = result['packages'].get('available', [])

            red_pack_info.update(
                status=1,
                redpacks=redpacks
            )
        else:
            red_pack_info.update(
                status=0,
                msg=u'authentic error!'
            )

        return Response(red_pack_info)

        # return HttpResponse(renderers.JSONRenderer().render(red_pack_info, 'application/json'))


class SendRedPacks(APIView):
    """
    http请求方式: post
    http://xxxxxx.com/php/redpacks/send/
    :return: status = 1  成功, status = 0 失败 .
    """
    permission_classes = ()

    def post(self, request):

        redpack_id = self.request.REQUEST.get('redpack_id')
        user_ids = self.request.REQUEST.get('userIds').split(',')

        if redpack_id and user_ids:
            ret = send_redpacks(redpack_id, user_ids)

        else:
            ret = {'status': 0,
                   'msg': 'args error!'}

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))


class GetAPPUser(APIView):
    """
    http请求方式: post
    http://xxxxxx.com/php/app/user/get/
    :return: status = 1  成功, status = 0 失败 .
    """
    permission_classes = ()

    def get(self, request):

        token = self.request.REQUEST.get('token')

        token = Token.objects.filter(key=token).first()
        if token:
            user_id = token.user.pk
            margin = token.user.margin.margin
            ret = {'status': 1,
                   'user_id': user_id,
                   'margin': margin}

        else:
            ret = {'status': 0,
                   'msg': 'token error!'}

        return HttpResponse(renderers.JSONRenderer().render(ret, 'application/json'))
