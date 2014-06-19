# encoding: utf-8
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from trade import P2PTrader
from models import P2PProduct, RecordCatalog
from exceptions import UserRestriction, ProductRestriction
# Create your tests here.


class P2PTestCase(TransactionTestCase):

    fixtures = ['user.json', 'p2p.json']

    def setUp(self):
        self.product0 = P2PProduct.objects.get(pk=241)
        self.product1 = P2PProduct.objects.get(pk=242)
        self.user0 = get_user_model().objects.get(pk=1)
        self.user1 = get_user_model().objects.get(pk=2)
        self.trader00 = P2PTrader(self.product0, self.user0)
        self.trader01 = P2PTrader(self.product0, self.user1)
        self.trader11 = P2PTrader(self.product1, self.user1)
        RecordCatalog.objects.create(name=u'申购', description=u'申购', catalog_id=1)


    def testUserRestriction(self):
        self.assertRaises(UserRestriction, self.trader00.purchase, (1001))
        self.assertRaises(UserRestriction, self.trader01.purchase, (468001))

    def testProductRestriction(self):
        self.assertRaises(ProductRestriction, self.trader00.purchase, (1.25))
        self.assertRaises(ProductRestriction, self.trader11.purchase, (80001))
        self.assertRaises(ProductRestriction, self.trader00.purchase, (-10))
        self.assertRaises(ProductRestriction, self.trader00.purchase, (0))

    def testP2PProductModelMethod(self):
        self.assertEqual(self.product1.remain, 80000)
        self.assertEqual(self.product1.completion_rate, 20)
        self.assertEqual(self.product1.limit_amount_per_user, 20000)
        self.assertTrue(self.product1.has_amount(80000))
        self.assertFalse(self.product1.has_amount(80001))

    def testUserMarginModelMethod(self):
        self.assertTrue(self.user0.usermargin.has_margin(1000))
        self.assertFalse(self.user0.usermargin.has_margin(1001))

    def testTradeRecord(self):
        catalog = RecordCatalog.objects.get(catalog_id=1)
        record = self.trader00.purchase(1000)
        self.assertIsNotNone(record)
        self.assertEqual(record.catalog, catalog)
        self.assertEqual(record.amount, 1000)
        self.assertEqual(record.product, self.product0)
        self.assertEqual(record.product_balance_before, 2340000)
        self.assertEqual(record.product_balance_after, 2339000)
        self.assertEqual(record.user, self.user0)
        self.assertEqual(record.user_margin_before, self.user0.usermargin.margin + 1000)
        self.assertEqual(record.user_margin_after, self.user0.usermargin.margin)
        self.assertEqual(record.operation_ip, '')
        self.assertEqual(record.operation_request_headers, '')
        self.assertEqual(record.checksum, '26f912b2de0e5d5f54e4ff556b5601c3b37224d75f1e3d35b5e7b41b190657abb14fa1e92e6c'
                                          'c432998ea0f05a04d74a257d8d16179246274c27ba89ac9bb0fa')


