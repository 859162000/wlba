# encoding: utf-8
import json
from datetime import date, datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User

from wanglibao_margin.models import Margin
from wanglibao_margin.marginkeeper import MarginKeeper

from mock_generator import MockGenerator
from models import P2PProduct, WarrantCompany, ProductAmortization, P2PEquity, UserAmortization
from trade import P2PTrader, P2POperator
from exceptions import P2PException
# Create your tests here.


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

    def testCreateProduct(self):
        product = P2PProduct(
            name=u'测试产品长名字102185-2004a', short_name=u'测试1', serial_number=u'110-220-59a', status=u'正在招标',
            period=3, expected_earning_rate=10, pay_method=u'等额本息', amortization_count=3, total_amount=100000,
            warrant_company=self.warrant_company
        )
        amo1 = ProductAmortization(
            term=1, term_date=datetime.now(), principal=10, interest=1, product=product
        )
        self.assertIsInstance(product, P2PProduct)
        self.assertIsInstance(amo1, ProductAmortization)

    def testWarrantCompany(self):
        warrant_company = WarrantCompany.objects.create(name=u'测试担保')
        self.assertIsInstance(warrant_company, WarrantCompany)

    def testPurchase(self):
        shuo_margin_keeper = MarginKeeper(self.users['shuo'])
        xihui_margin_keeper = MarginKeeper(self.users['xihui'])
        shuo_margin_keeper.deposit(100000)
        xihui_margin_keeper.deposit(10000)
        operator = P2POperator()

        product = MockGenerator.generate_staging_p2p(u'测试用P2P产品第一号', 10000, per_user=0.5)
        self.assertEqual(product.total_amount, 10000)
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

