#!/usr/bin/env python
# encoding: utf-8
import logging
from django.contrib.auth.models import User

from django.db import transaction
from django.utils import timezone
from marketing import tools
#from marketing.models import IntroducedBy, Reward, RewardRecord
from order.models import Order
from django.conf import settings
#from wanglibao.templatetags.formatters import safe_phone_str
from wanglibao_reward.views import RewardDistributer
from wanglibao_account.cooperation import CoopRegister
from wanglibao_margin.marginkeeper import MarginKeeper
from order.utils import OrderHelper
from keeper import ProductKeeper, EquityKeeper, AmortizationKeeper, EquityKeeperDecorator
from exceptions import P2PException
from wanglibao_p2p.models import P2PProduct, P2PEquity
from wanglibao_sms import messages
from wanglibao_sms.tasks import send_messages
from wanglibao_account import message as inside_message
from wanglibao_redpack import backends as redpack_backends
from wanglibao_redpack.models import RedPackRecord
import logging
# from wanglibao_account.utils import CjdaoUtils
# from wanglibao_account.tasks import cjdao_callback
# from wanglibao.settings import CJDAOKEY, RETURN_PURCHARSE_URL
import re
import json, datetime

from wanglibao_redis.backend import redis_backend

from wanglibao_rest.utils import split_ua
from weixin.models import WeixinUser
from weixin.constant import PRODUCT_INVEST_SUCCESS_TEMPLATE_ID
from weixin.tasks import sentTemplate
from wanglibao_reward.utils import processMarchAwardAfterP2pBuy

logger = logging.getLogger('wanglibao_account')

class P2PTrader(object):
    def __init__(self, product, user, order_id=None, request=None):
        self.user = user
        self.product = product
        
        if self.product.status != u"正在招标":
            raise P2PException(u'购买的标不在招标状态')

        self.request = request
        if order_id is None:
            self.order_id = OrderHelper.place_order(user, order_type=u'产品申购', product_id=product.id, status=u'新建').id
        else:
            self.order_id = order_id
        self.margin_keeper = MarginKeeper(user=user, order_id=self.order_id)
        self.product_keeper = ProductKeeper(product, order_id=self.order_id)
        self.equity_keeper = EquityKeeper(user=user, product=product, order_id=self.order_id)
        if request:
            self.device = split_ua(request)
            self.device_type = self.device['device_type']
        else:
            self.device = split_ua(request)
            self.device_type = "pc"

    def purchase(self, amount, redpack=0, platform=u''):
        description = u'购买P2P产品 %s %s 份' % (self.product.short_name, amount)
        is_full = False
        if self.user.wanglibaouserprofile.frozen:
            raise P2PException(u'用户账户已冻结，请联系客服')
        with transaction.atomic():
            if redpack:
                # 为防止用户同时打开两个浏览器同时使用加息券和红包，须先检测
                coupons = RedPackRecord.objects.filter(user=self.user, product_id=self.product.id) \
                    .filter(redpack__event__rtype='interest_coupon')
                if coupons:
                    raise P2PException(u'已经选择过加息券，不能重复或叠加使用')
                else:
                    this_redpack = RedPackRecord.objects.filter(pk=redpack).first()
                    this_rtype = this_redpack.redpack.event.rtype
                    coupons = RedPackRecord.objects.filter(user=self.user, product_id=self.product.id) \
                        .exclude(redpack__event__rtype='interest_coupon')
                    if coupons and this_rtype == 'interest_coupon':
                        raise P2PException(u'红包和加息券不能同时叠加使用')

                redpack_order_id = OrderHelper.place_order(self.user, order_type=u'优惠券消费', redpack=redpack,
                                                           product_id=self.product.id, status=u'新建').id
                result = redpack_backends.consume(redpack, amount, self.user, self.order_id, self.device_type, self.product.id)
                if result['ret_code'] != 0:
                    raise Exception,result['message']
                if result['rtype'] != 'interest_coupon':
                    red_record = self.margin_keeper.redpack_deposit(result['deduct'], u"购买P2P抵扣%s元" % result['deduct'],
                                                                    order_id=redpack_order_id, savepoint=False)
                OrderHelper.update_order(Order.objects.get(pk=redpack_order_id), user=self.user, status=u'成功', 
                                        amount=amount, deduct=result['deduct'], redpack=redpack)

            product_record = self.product_keeper.reserve(amount, self.user, savepoint=False, platform=platform)
            margin_record = self.margin_keeper.freeze(amount, description=description, savepoint=False)
            equity = self.equity_keeper.reserve(amount, description=description, savepoint=False)

            OrderHelper.update_order(Order.objects.get(pk=self.order_id), user=self.user, status=u'份额确认', amount=amount)

            if product_record.product_balance_after <= 0:
                is_full = True

        # fix@chenweibin, add order_id
        # Modify by hb on 2015-11-25 : add "try-except"
        try:
            logger.debug("=20151125= decide_first.apply_async : [%s], [%s], [%s], [%s], [%s], [%s]" % \
                         (self.user.id, amount, self.device['device_type'], self.order_id, self.product.id, is_full) )
            tools.decide_first.apply_async(kwargs={"user_id": self.user.id, "amount": amount,
                                                   "device": self.device, "order_id": self.order_id,
                                                   "product_id": self.product.id, "is_full": is_full})
        except Exception, reason:
            logger.debug("=20151125= decide_first.apply_async Except:{0}".format(reason))
            pass

        try:
            logger.debug("=20151125= CoopRegister.process_for_purchase : [%s], [%s]" % (self.user.id, self.order_id) )
            CoopRegister(self.request).process_for_purchase(self.user, self.order_id)
        except Exception, reason:
            logger.debug("=20151125= CoopRegister.process_for_purchase Except:{0}".format(reason) )
            pass

        try:
            logger.debug("=20151125= RewardDistributer.processor_for_distribute : [%s], [%s]" % (self.user.id, self.order_id) )
            kwargs = {
                'amount': amount,
                'order_id': self.order_id,
                'user': self.user,}

            RewardDistributer(self.request, kwargs).processor_for_distribute()
        except Exception, reason:
            logger.debug("=20151125= RewardDistributer.processor_for_distribute Except:{0}".format(reason) )
            pass
        else:
            logger.debug("=20151125= RewardDistributer.processor_for_distribute : {0}购标成功".format(self.user) )

        # 投标成功发站内信
        matches = re.search(u'日计息', self.product.pay_method)
        if matches and matches.group():
            pname = u"%s,期限%s天" % (self.product.name, self.product.period)
        else:
            pname = u"%s,期限%s个月" % (self.product.name, self.product.period)

        title, content = messages.msg_bid_purchase(self.order_id, pname, amount)
        inside_message.send_one.apply_async(kwargs={
            "user_id": self.user.id,
            "title": title,
            "content": content,
            "mtype": "purchase"

        })
        logger.debug("=20151125= inside_message.send_one : {0}购标站内信发成功".format(self.user) )

        # 满标给管理员发短信
        if is_full:
            from wanglibao_p2p.tasks import full_send_message
            full_send_message.apply_async(kwargs={"product_name": self.product.name})

            if self.product.types.name != u'其他':
                # 检测是否有同类型的正在招标状态的标,有的话按照发布时间的顺序更改第一个标的发布时间为当前时间
                from wanglibao_p2p.tasks import p2p_auto_published_by_publish_time
                p2p_auto_published_by_publish_time(self.product.pay_method, self.product.period)

            # 满标将标信息写入redis
            cache_backend = redis_backend()
            if cache_backend._is_available():
                if not cache_backend.redis.exists("p2p_detail_{0}".format(self.product.id)):
                    cache_backend.get_cache_p2p_detail(self.product.id)

                # 将标写入redis list
                cache_backend.push_p2p_products(self.product)
        try:
            weixin_user = WeixinUser.objects.filter(user=self.user).first()
            now = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
            #         投标成功通知
            #         您好，您已投标成功。
            #         标的编号：10023
            #         投标金额：￥3000.00
            #         投标时间：2015-09-12
            #         投标成功,可在投标记录里查看.
            # {{first.DATA}} 标的编号：{{keyword1.DATA}} 投标金额：{{keyword2.DATA}} 投标时间：{{keyword3.DATA}} {{remark.DATA}}
            if weixin_user:
                sentTemplate.apply_async(kwargs={
                                "kwargs":json.dumps({
                                                "openid": weixin_user.openid,
                                                "template_id": PRODUCT_INVEST_SUCCESS_TEMPLATE_ID,
                                                "keyword1": self.product.name,
                                                "keyword2": "%s 元"%str(amount),
                                                "keyword3": now,
                                                "url":settings.CALLBACK_HOST + '/weixin/activity_ggl/?order_id=%s' % (self.order_id),
                                                "remark": u'恭喜您获得3次刮奖机会，速来戳"详情"拼运气!'
                                                    })},
                                                queue='celery02')

        except Exception, e:
            logger.debug("=====sentTemplate=================%s"%e.message)

        processMarchAwardAfterP2pBuy(self.user, self.product, self.order_id, amount)

        return product_record, margin_record, equity


class P2POperator(object):
    """
    When generate new entries, pls note that old entries may still exists, so remove them first
    """

    logger = logging.getLogger('p2p')

    @classmethod
    def watchdog(cls):
        print('Getting products with status 满标待处理')
        for product in P2PProduct.objects.filter(status=u'满标已打款'):
            try:
                cls().preprocess_for_settle(product)
            except P2PException, e:
                cls.logger.error(u'%s, %s' % (product.id, e.message))

        print('Getting products with status 满标已审核')
        for product in P2PProduct.objects.filter(status=u'满标已审核'):
            try:
                cls().settle(product)
            except P2PException, e:
                cls.logger.error(u'%s, %s' % (product.id, e.message))

        print('Getting products with status 正在招标 and end time earlier than now')
        for product in P2PProduct.objects.filter(status=u'正在招标', end_time__lte=timezone.now()):
            try:
                cls.fail(product)
            except P2PException, e:
                cls.logger.error(u'%s, %s' % (product.id, e.message))

        print('Getting amortization needs handle')
        amortizations_to_settle = AmortizationKeeper.get_ready_for_settle()
        print 'Get %d amortizations' % len(amortizations_to_settle)
        for amortization in amortizations_to_settle:
            try:
                cls().amortize(amortization)
            except P2PException, e:
                cls.logger.error(u'%s, %s' % (amortization, e.message))

        ## 停止在watchdog中每分钟循环自动投标，减轻celery任务
        ## 将自动投标入口改在两处，一是标状态变成“正在招标”，二是用户保存并启用自动投标配置
        print('Getting automation trades')
        from wanglibao_p2p.automatic import Automatic
        Automatic().auto_trade()

    @classmethod
    #@transaction.commit_manually
    def preprocess_for_settle(cls, product):
        cls.logger.info('Enter pre process for settle for product: %d: %s', product.id, product.name)

        # Create an order to link all changes
        order = OrderHelper.place_order(order_type=u'满标状态预处理', status=u'开始', product_id=product.id)
        if product.status != u'满标已打款':
            raise P2PException(u'产品状态(%s)不是(满标已打款)' % product.status)
        with transaction.atomic():
            # Generate the amotization plan and contract for each equity(user)
            amo_keeper = AmortizationKeeper(product, order_id=order.id)

            amo_keeper.generate_amortization_plan(savepoint=False)

            # for equity in product.equities.all():
            #     EquityKeeper(equity.user, equity.product, order_id=order.id).generate_contract(savepoint=False)
            # EquityKeeperDecorator(product, order.id).generate_contract(savepoint=False)

            product = P2PProduct.objects.get(pk=product.id)
            product.status = u'满标待审核'
            product.make_loans_time = timezone.now()
            product.save()

    @classmethod
    def settle(cls, product):
        if product.ordered_amount != product.total_amount:
            raise P2PException(u'产品已申购额度(%s)不等于总额度(%s)' % (str(product.ordered_amount), str(product.total_amount)))
        if product.status != u'满标已审核':
            raise P2PException(u'产品状态(%s)不是(满标已审核)' % product.status)

        phones = []
        messages_list = []
        user_ids = []
        with transaction.atomic():
            for equity in product.equities.all():
                equity_keeper = EquityKeeper(equity.user, equity.product)
                equity_keeper.settle(savepoint=False)

                user_ids.append(equity.user.id)
                phones.append(equity.user.wanglibaouserprofile.phone)
                name = equity.user.wanglibaouserprofile.name
                messages_list.append(messages.product_settled(name, equity, product, timezone.now()))

            product.status = u'还款中'
            product.save()

        send_messages.apply_async(kwargs={
            "phones": phones,
            "messages": messages_list,
        })

        user_ids = {}.fromkeys(user_ids).keys()

        matches = re.search(u'日计息', product.pay_method)
        if matches and matches.group():
            pname = u"%s,期限%s天" % (product.name, product.period)
        else:
            pname = u"%s,期限%s个月" % (product.name, product.period)
        title, content = messages.msg_bid_success(pname, timezone.now())
        inside_message.send_batch.apply_async(kwargs={
            "users": user_ids,
            "title": title,
            "content": content,
            "mtype": "loaned"
        })

        cache_backend = redis_backend()
        # 更新该标的redis缓存
        cache_backend.update_detail_cache(product.id)

        # 将标信息从满标的redis列表中挪到还款中的redis列表
        cache_backend.update_list_cache('p2p_products_full', 'p2p_products_repayment', product)

    @classmethod
    def fail(cls, product):
        if product.status == u'流标':
            raise P2PException('Product already failed')

        cls.logger.info(u"Product [%d] [%s] not able to reach 100%%" % (product.id, product.name))
        user_ids = []
        phones = []
        messages_list = []

        with transaction.atomic():
            for equity in product.equities.all():
                equity_keeper = EquityKeeper(equity.user, equity.product)
                equity_keeper.rollback(savepoint=False)

                user_ids.append(equity.user.id)
                phones.append(equity.user.wanglibaouserprofile.phone)
                messages_list.append(messages.product_failed(equity.user.wanglibaouserprofile.name, product))
            ProductKeeper(product).fail()

        user_ids = {}.fromkeys(user_ids).keys()
        if phones:
            send_messages.apply_async(kwargs={
                "phones": phones,
                "messages": messages_list,
            })

            matches = re.search(u'日计息', product.pay_method)
            if matches and matches.group():
                pname = u"%s,期限%s天" % (product.name, product.period)
            else:
                pname = u"%s,期限%s个月" % (product.name, product.period)
            title, content = messages.msg_bid_fail(pname)
            inside_message.send_batch.apply_async(kwargs={
                "users": user_ids,
                "title": title,
                "content": content,
                "mtype": "bids"
            })

    @classmethod
    def amortize(cls, amortization):
        if not amortization.ready_for_settle:
            raise P2PException('not ready for settle')
        if amortization.product.status != u'还款中':
            raise P2PException('not in pay status')
        with transaction.atomic():
            amo_keeper = AmortizationKeeper(amortization.product)
            amo_keeper.amortize(amortization)

            product = amortization.product
            all_settled = reduce(lambda flag, a: flag & a.settled, product.amortizations.all(), True)

            if all_settled:
                # cls.settle_hike(product)
                # cls.logger.info("Product [%s] [%s] paid hike", product.id, product.name)

                cls.logger.info("Product [%d] [%s] payed all amortizations, finish it", product.id, product.name)
                ProductKeeper(product).finish(None)

                cache_backend = redis_backend()
                # 更新该标的redis缓存
                cache_backend.update_detail_cache(product.id)

                # 将标信息从还款中的redis列表中挪到已完成的redis列表
                cache_backend.update_list_cache('p2p_products_repayment', 'p2p_products_finished', product)

    @classmethod
    def settle_hike(cls, product):
        result = redpack_backends.settle_hike(product)
        if not result:
            return
        for x in result:
            order_id = OrderHelper.place_order(x['user'], order_type=u'加息', product_id=product.id, status=u'新建').id
            margin_keeper = MarginKeeper(user=x['user'], order_id=order_id)
            margin_keeper.hike_deposit(x['amount'], u"加息存入%s元" % x['amount'], savepoint=False)
            OrderHelper.update_order(Order.objects.get(pk=order_id), user=x['user'], status=u'成功', amount=x['amount'])
