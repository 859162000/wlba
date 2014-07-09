# coding=utf-8
from django.test import TestCase
from order.models import Order
from order.utils import OrderHelper


class OrderTest(TestCase):
    def test_order(self):
        order = OrderHelper.place_order(type=u'充值', product_id='1234123')
        self.assertTrue(order.id >= 0)
        self.assertEqual(order.extra_data['product_id'], '1234123')

        order = OrderHelper.update_order(order, status=u'关闭')
        self.assertEqual(order.status, u'关闭')

        sub_order = OrderHelper.place_order(type=u'充值', somekey='value')
        sub_order.parent = order

        sub_order.save()

        order = Order.objects.get(pk=order.id)
        self.assertEqual(len(order.children.all()), 1)
