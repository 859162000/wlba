#!/usr/bin/env python
# encoding: utf-8

from django.db import transaction
from order.utils import OrderHelper
from order.models import Order
from wanglibao_p2p.trade import P2PTrader as P2PTraderBase
from wanglibao_p2p.exceptions import P2PException
from wanglibao_redis.backend import redis_backend


class P2PTrader(P2PTraderBase):
    def __init__(self, **kwargs):
        super(P2PTrader, self).__init__(**kwargs)

    def purchase(self, amount, redpack=0, platform=u''):
        description = u'购买P2P产品 %s %s 份' % (self.product.short_name, amount)
        is_full = False
        if self.user.wanglibaouserprofile.frozen:
            raise P2PException(u'用户账户已冻结，请联系客服')
        with transaction.atomic():
            product_record = self.product_keeper.reserve(amount, self.user, savepoint=False, platform=platform)
            margin_record = self.margin_keeper.freeze(amount, description=description, savepoint=False)
            equity = self.equity_keeper.reserve(amount, description=description, savepoint=False)

            OrderHelper.update_order(Order.objects.get(pk=self.order_id), user=self.user, status=u'份额确认', amount=amount)

            if product_record.product_balance_after <= 0:
                is_full = True

        # 投标成功给用户内信
        # FixMe

        # 满标给管理员发短信
        if is_full:
            from wanglibao_p2p.tasks import full_send_message
            full_send_message.apply_async(kwargs={"product_name": self.product.name})

            if self.product.types.name != u'其他':
                # 检测是否有同类型的正在招标状态的标,有的话按照发布时间的顺序更改第一个标的发布时间为当前时间
                from wanglibao_p2p.tasks import p2p_auto_published_by_publish_time
                p2p_auto_published_by_publish_time(self.product.pay_method, self.product.period)

            # 满标将标信息写入redis
            cache_backend = redis_backend()
            if cache_backend._is_available():
                if not cache_backend.redis.exists("p2p_detail_{0}".format(self.product.id)):
                    cache_backend.get_cache_p2p_detail(self.product.id)

                # 将标写入redis list
                cache_backend.push_p2p_products(self.product)

        return product_record, margin_record, equity
