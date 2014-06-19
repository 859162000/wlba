from django.test import TestCase
from order.utils import OrderHelper


class OrderTest(TestCase):
    def test_order(self):
        order = OrderHelper.place_order(type='charge', product_id='1234123')
        self.assertTrue(order.id >= 0)

        order = OrderHelper.update_order(order, status='closed')
        self.assertEqual(order.status, 'closed')
