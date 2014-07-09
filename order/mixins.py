from order.utils import OrderHelper


class KeeperBaseMixin(object):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.get('user', None)

        order_id = kwargs.get('order_id', None)
        if order_id is None:
            order_id = OrderHelper.place_order(user=self.user).id

        self.order_id = order_id
