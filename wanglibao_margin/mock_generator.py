from django.contrib.auth import get_user_model
from order.utils import OrderHelper
from wanglibao_margin.keeper import Keeper
from wanglibao_margin.models import Margin


class MockGenerator(object):
    @classmethod
    def generate(cls, clean=False):
        User = get_user_model()

        users = User.objects.all()

        for u in users:
            if not hasattr(u, 'margin'):
                margin = Margin(user=u)
                margin.save()

        for u in users:
            order = OrderHelper.place_order()
            keeper = Keeper(order=order.id, user=u)
            keeper.deposit(100000000)

