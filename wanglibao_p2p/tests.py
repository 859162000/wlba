# encoding: utf-8
from datetime import date, datetime
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from order.models import Order
from order.utils import OrderHelper

from wanglibao_margin.marginkeeper import MarginKeeper

from mock_generator import MockGenerator
from models import P2PProduct, WarrantCompany, ProductAmortization, P2PEquity, UserAmortization, P2PRecord, EquityRecord
from trade import P2PTrader, P2POperator
from exceptions import P2PException
# Create your tests here.
from wanglibao_margin.models import MarginRecord


class TraderTestCase(TransactionTestCase):

    def setUp(self):
        self.user1 = User.objects.create(username='user1')
        self.user2 = User.objects.create(username='user2')
        self.warrant_company = WarrantCompany.objects.create(name=u'肯定会还钱的担保公司')

    def testPurchase(self):
        user1_margin_keeper = MarginKeeper(self.user1)
        user1_margin_keeper.deposit(100000)

        product = MockGenerator.generate_staging_p2p(u'test', 100000, per_user=0.1)
        user1_trader = P2PTrader(product, self.user1)
        user1_trader.purchase(1000)

        margin_records = MarginRecord.objects.all()
        self.assertEqual(len(margin_records), 2)

        for margin_record in margin_records:
            self.assertIsNotNone(margin_record.order_id)

        order = Order.objects.get(pk=user1_trader.order_id)
        notes = order.notes.all()

        self.assertEqual(len(notes), 2)

        self.assertEqual(notes[0].extra_data['status'], u'份额确认')

    def testPreProcess(self):
        user1_margin_keeper = MarginKeeper(self.user1)
        user1_margin_keeper.deposit(100000)

        product = MockGenerator.generate_staging_p2p(u'test', 100000, per_user=1)
        user1_trader = P2PTrader(product, self.user1)
        user1_trader.purchase(100000)

        product = P2PProduct.objects.get(pk=product.id)

        # Now The product status should be pre settle, which means some one should do the final check,
        # Do money transfer, and if everything works, then he or she should change status to 还款中
        product = P2PProduct.objects.get(pk=product.id)
        self.assertEqual(product.status, u'满标待处理')

        operator = P2POperator()
        operator.preprocess_for_settle(product=product)

        product = P2PProduct.objects.get(pk=product.id)
        self.assertEqual(product.status, u'满标待审核')

        # Now the equity should has contract, user should has amortization plan
        equity = P2PEquity.objects.filter(user=self.user1, product=product).first()

        try:
            f = equity.contract.open('r')
        except ValueError, e:
            self.fail("The contract not generated as expected")

    def testSettle(self):
        user1_margin_keeper = MarginKeeper(self.user1)
        user1_margin_keeper.deposit(100000)

        product = MockGenerator.generate_staging_p2p(u'test', 100000, per_user=1)
        user1_trader = P2PTrader(product, self.user1)
        user1_trader.purchase(100000)

        product = P2PProduct.objects.get(pk=product.id)

        # Now The product status should be pre settle, which means some one should do the final check,
        # Do money transfer, and if everything works, then he or she should change status to 还款中
        product = P2PProduct.objects.get(pk=product.id)
        self.assertEqual(product.status, u'满标待处理')

        operator = P2POperator()
        operator.preprocess_for_settle(product=product)

        product = P2PProduct.objects.get(pk=product.id)
        self.assertEqual(product.status, u'满标待审核')

        # Now the equity should has contract, user should has amortization plan
        equity = P2PEquity.objects.filter(user=self.user1, product=product).first()

        try:
            f = equity.contract.open('r')
        except ValueError, e:
            self.fail("The contract not generated as expected")

        # Simulate user audited and set status to 还款中
        product.status = u'满标已审核'
        product.save()

        operator.settle(product)

    def testFullProcess(self):
        user1_margin_keeper = MarginKeeper(self.user1)
        user2_margin_keeper = MarginKeeper(self.user2)
        user1_margin_keeper.deposit(100000)
        user2_margin_keeper.deposit(10000)
        operator = P2POperator()

        product = MockGenerator.generate_staging_p2p(u'测试用P2P产品第一号', 10000, per_user=0.5)
        user1_trader = P2PTrader(product, self.user1)
        # test purchase
        user1_trader.purchase(5000)
        # test per_user_limit restriction
        self.assertRaises(P2PException, user1_trader.purchase, 1)
        product = P2PProduct.objects.first()
        self.assertEqual(product.ordered_amount, 5000)
        self.assertEqual(product.remain, 5000)
        self.assertEqual(product.completion_rate, 50)
        # test user equity
        user1_equity = P2PEquity.objects.get(user=self.user1, product=product)
        self.assertEqual(user1_equity.equity, 5000)
        self.assertFalse(user1_equity.confirm)
        self.assertEqual(user1_equity.ratio, 0.5)
        # complete the product
        self.assertRaises(P2PException, operator.over, product)
        user2_trader = P2PTrader(product, self.user2)
        user2_trader.purchase(5000)
        product = P2PProduct.objects.first()
        operator.over(product)
        product = P2PProduct.objects.first()
        self.assertEqual(product.status, u'已满标')
        operator.settle(product)
        product = P2PProduct.objects.first()
        self.assertEqual(product.status, u'还款中')
        user2_equity = P2PEquity.objects.get(product=product, user=self.user2)
        user1_equity = P2PEquity.objects.get(product=product, user=self.user1)
        self.assertEqual(user2_equity.equity, 5000)
        self.assertTrue(user2_equity.confirm)
        self.assertEqual(user1_equity.equity, 5000)
        self.assertTrue(user1_equity.confirm)
        # test user amortizations
        user1_amortizations = UserAmortization.objects.filter(user=self.user1)
        user2_amortizations = UserAmortization.objects.filter(user=self.user2)
        self.assertEqual(user1_amortizations.count(), 3)
        self.assertEqual(user2_amortizations.count(), 3)

        # Check records, we need to make sure that all changes are recorded
        records = P2PRecord.objects.all().filter(product=product)
        self.assertEqual(len(records), 2)

        margin_records = MarginRecord.objects.all().filter(user=self.user1)
        self.assertEqual(len(margin_records), 3)

        for margin_record in margin_records:
            self.assertIsNotNone(margin_record.order_id)

        equity_records = EquityRecord.objects.all().filter(user=self.user1)
        self.assertEqual(len(equity_records), 2)


