# encoding: utf-8
from django.test import TransactionTestCase
from django.contrib.auth.models import User

from order.models import Order
from wanglibao_margin.marginkeeper import MarginKeeper
from mock_generator import MockGenerator
from models import P2PProduct, WarrantCompany, P2PEquity
from trade import P2PTrader, P2POperator

# Create your tests here.
from wanglibao_margin.models import MarginRecord
from wanglibao_p2p.keeper import ProductKeeper


class TraderTestCase(TransactionTestCase):

    def setUp(self):
        self.user1 = User.objects.create(username='user1')
        self.user2 = User.objects.create(username='user2')
        self.warrant_company = WarrantCompany.objects.create(name=u'肯定会还钱的担保公司')

    def test_purchase(self):
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

    def test_pre_process(self):
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

    def test_settle(self):
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

    def test_full_process(self):
        user1_margin_keeper = MarginKeeper(self.user1)
        user1_margin_keeper.deposit(100000)
        operator = P2POperator()

        product = MockGenerator.generate_staging_p2p(u'测试用P2P产品第一号', 100000, per_user=1)

        # Run the operator and check nothing happened

        P2PTrader(product, self.user1).purchase(100000)

        product = P2PProduct.objects.first()
        self.assertEqual(product.status, u'满标待处理')

        # Run the operator and check status -> 满标待审核
        operator.watchdog()

        # 满标待审核 -> 满标已审核
        product = P2PProduct.objects.first()
        ProductKeeper(product).audit(self.user1)

        # status -> 还款中
        operator.watchdog()
        product = P2PProduct.objects.get(pk=product.id)
        self.assertEqual(product.status, u'还款中')

        for a in product.amortizations.all():
            a.ready_for_settle = True
            a.save()
            operator.watchdog()

        product = P2PProduct.objects.get(pk=product.id)
        self.assertEqual(product.status, u'已完成')
