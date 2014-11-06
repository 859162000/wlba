# encoding: utf-8
import logging
from django.db import transaction
from django.utils import timezone
from marketing.models import IntroducedBy
from order.models import Order
from wanglibao.templatetags.formatters import safe_phone_str
from wanglibao_margin.marginkeeper import MarginKeeper
from order.utils import OrderHelper
from keeper import ProductKeeper, EquityKeeper, AmortizationKeeper
from exceptions import P2PException
from wanglibao_p2p.models import P2PProduct
from wanglibao_sms import messages
from wanglibao_sms.tasks import send_messages


class P2PTrader(object):

    def __init__(self, product, user, order_id=None, request=None):
        self.user = user
        self.product = product
        self.request = request
        if order_id is None:
            self.order_id = OrderHelper.place_order(user, order_type=u'产品申购', product_id=product.id, status=u'新建').id
        else:
            self.order_id = order_id
        self.margin_keeper = MarginKeeper(user=user, order_id=self.order_id)
        self.product_keeper = ProductKeeper(product, order_id=self.order_id)
        self.equity_keeper = EquityKeeper(user=user, product=product, order_id=self.order_id)

    def purchase(self, amount):
        description = u'购买P2P产品 %s %s 份' %(self.product.short_name, amount)
        if self.user.wanglibaouserprofile.frozen:
            raise P2PException(u'用户账户已冻结，请联系客服')
        with transaction.atomic():
            product_record = self.product_keeper.reserve(amount, self.user, savepoint=False)
            margin_record = self.margin_keeper.freeze(amount, description=description, savepoint=False)
            equity = self.equity_keeper.reserve(amount, description=description, savepoint=False)

            OrderHelper.update_order(Order.objects.get(pk=self.order_id), user=self.user, status=u'份额确认', amount=amount)

        introduced_by = IntroducedBy.objects.filter(user=self.user).first()
        #phone_verified 渠道客户判断
        if introduced_by and introduced_by.bought_at is None:
            introduced_by.bought_at = timezone.now()
            introduced_by.save()

            if "channel" not in introduced_by.introduced_by.username:
                inviter_phone = introduced_by.introduced_by.wanglibaouserprofile.phone
                invited_phone = introduced_by.user.wanglibaouserprofile.phone
                if amount >= 1000:
                    send_messages.apply_async(kwargs={
                        "phones": [inviter_phone, invited_phone],
                        "messages": [messages.gift_inviter(invited_phone=safe_phone_str(invited_phone), money=30),
                                     messages.gift_invited(inviter_phone=safe_phone_str(inviter_phone), money=30)]
                    })

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

    @classmethod
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

            for equity in product.equities.all():
                EquityKeeper(equity.user, equity.product, order_id=order.id).generate_contract(savepoint=False)

            product = P2PProduct.objects.get(pk=product.id)
            product.status = u'满标待审核'
            product.save()

    @classmethod
    def settle(cls, product):
        if product.ordered_amount != product.total_amount:
            raise P2PException(u'产品已申购额度(%s)不等于总额度(%s)' % (str(product.ordered_amount), str(product.total_amount)))
        if product.status != u'满标已审核':
            raise P2PException(u'产品状态(%s)不是(满标已审核)' % product.status)
        with transaction.atomic():
            for equity in product.equities.all():
                equity_keeper = EquityKeeper(equity.user, equity.product)
                equity_keeper.settle(savepoint=False)
            product.status = u'还款中'
            product.save()

        product = P2PProduct.objects.get(id=product.id)
        phones = [e.user.wanglibaouserprofile.phone for e in product.equities.all().prefetch_related('user').prefetch_related('user__wanglibaouserprofile')]
        send_messages.apply_async(kwargs={
            "phones": phones,
            "messages": [messages.product_settled(product, timezone.now())]
        })

    @classmethod
    def fail(cls, product):
        if product.status == u'流标':
            raise P2PException('Product already failed')

        cls.logger.info(u"Product [%d] [%s] not able to reach 100%%" % (product.id, product.name))
        with transaction.atomic():
            for equity in product.equities.all():
                equity_keeper = EquityKeeper(equity.user, equity.product)
                equity_keeper.rollback(savepoint=False)
            ProductKeeper(product).fail()

        product = P2PProduct.objects.get(id=product.id)
        phones = [equity.user.wanglibaouserprofile.phone for equity in product.equities.all().prefetch_related('user').prefetch_related('user__wanglibaouserprofile')]
        if phones:
            send_messages.apply_async(kwargs={
                "phones": phones,
                "messages": [messages.product_failed(product)]
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
                cls.logger.info("Product [%d] [%s] payed all amortizations, finish it", product.id, product.name)
                ProductKeeper(product).finish(None)
