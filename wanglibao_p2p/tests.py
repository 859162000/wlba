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
        self.users = dict()
        self.users['shuo'] = User.objects.create(username='shuo')
        self.users['xihui'] = User.objects.create(username='xihui')
        self.users['yixiong'] = User.objects.create(username='yixion')
        self.users['li7'] = User.objects.create(username='liqi')
        self.users['tongtong'] = User.objects.create(username='tongtong')
        self.warrant_company = WarrantCompany.objects.create(name=u'肯定会还钱的担保公司')

    def testUserMargin(self):
        self.assertEqual(self.users['shuo'].margin.margin, 0)

    def testPurchase(self):
        shuo_margin_keeper = MarginKeeper(self.users['shuo'])
        shuo_margin_keeper.deposit(100000)

        product = MockGenerator.generate_staging_p2p(u'test', 100000, per_user=0.1)
        shuo_trader = P2PTrader(product, self.users['shuo'])
        shuo_trader.purchase(1000)

        margin_records = MarginRecord.objects.all()
        self.assertEqual(len(margin_records), 2)

        for margin_record in margin_records:
            self.assertIsNotNone(margin_record.order_id)

        order = Order.objects.get(pk=shuo_trader.order_id)
        notes = order.notes.all()

        self.assertEqual(len(notes), 2)

        self.assertEqual(notes[0].extra_data['status'], u'份额确认')


    def testFullProcess(self):
        shuo_margin_keeper = MarginKeeper(self.users['shuo'])
        xihui_margin_keeper = MarginKeeper(self.users['xihui'])
        shuo_margin_keeper.deposit(100000)
        xihui_margin_keeper.deposit(10000)
        operator = P2POperator()

        product = MockGenerator.generate_staging_p2p(u'测试用P2P产品第一号', 10000, per_user=0.5)
        shuo_trader = P2PTrader(product, self.users['shuo'])
        # test purchase
        shuo_trader.purchase(5000)
        # test per_user_limit restriction
        self.assertRaises(P2PException, shuo_trader.purchase, 1)
        product = P2PProduct.objects.first()
        self.assertEqual(product.ordered_amount, 5000)
        self.assertEqual(product.remain, 5000)
        self.assertEqual(product.completion_rate, 50)
        # test user equity
        shuo_equity = P2PEquity.objects.get(user=self.users['shuo'], product=product)
        self.assertEqual(shuo_equity.equity, 5000)
        self.assertFalse(shuo_equity.confirm)
        self.assertEqual(shuo_equity.ratio, 0.5)
        # complete the product
        self.assertRaises(P2PException, operator.over, product)
        xihui_trader = P2PTrader(product, self.users['xihui'])
        xihui_trader.purchase(5000)
        product = P2PProduct.objects.first()
        operator.over(product)
        product = P2PProduct.objects.first()
        self.assertEqual(product.status, u'已满标')
        operator.settle(product)
        product = P2PProduct.objects.first()
        self.assertEqual(product.status, u'还款中')
        xihui_equity = P2PEquity.objects.get(product=product, user=self.users['xihui'])
        shuo_equity = P2PEquity.objects.get(product=product, user=self.users['shuo'])
        self.assertEqual(xihui_equity.equity, 5000)
        self.assertTrue(xihui_equity.confirm)
        self.assertEqual(shuo_equity.equity, 5000)
        self.assertTrue(shuo_equity.confirm)
        # test user amortizations
        shuo_amortizations = UserAmortization.objects.filter(user=self.users['shuo'])
        xihui_amortizations = UserAmortization.objects.filter(user=self.users['xihui'])
        self.assertEqual(shuo_amortizations.count(), 3)
        self.assertEqual(xihui_amortizations.count(), 3)

        # Check records, we need to make sure that all changes are recorded
        records = P2PRecord.objects.all().filter(product=product)
        self.assertEqual(len(records), 2)

        margin_records = MarginRecord.objects.all().filter(user=self.users['shuo'])
        self.assertEqual(len(margin_records), 3)

        for margin_record in margin_records:
            self.assertIsNotNone(margin_record.order_id)

        equity_records = EquityRecord.objects.all().filter(user=self.users['shuo'])
        self.assertEqual(len(equity_records), 2)


