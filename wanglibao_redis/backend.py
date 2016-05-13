# encoding:utf-8

import json
import redis
from django.conf import settings
from common.tools import serialize_instance, deserialize_instance
from wanglibao_p2p.models import P2PProduct


class RedisBackend(object):
    def __init__(self, host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB):
        try:
            self.password = settings.REDIS_PASSWORD
            self.pool = redis.ConnectionPool(host=host, port=port, db=db, password=self.password)
            self.redis = redis.Redis(connection_pool=self.pool)
            self.redis.set("test", "test")
        except:
            self.pool = None
            self.redis = None

    def _is_available(self):
        try:
            self.redis.ping()
            return True
        except:
            return False

    def _exists(self, name):
        if self.redis:
            return self.redis.exists(name)
        return False

    def _set(self, key, value):
        if self.redis:
            self.redis.set(key, value)

    def _get(self, key):
        if self.redis:
            return self.redis.get(key)
        return None

    def _delete(self, key):
        if self.redis:
            self.redis.delete(key)

    def _lpush(self, key, value):
        if self.redis:
            self.redis.lpush(key, value)

    def _rpush(self, key, value):
        if self.redis:
            self.redis.rpush(key, value)

    def _lrange(self, key, start, end):
        if self.redis:
            return self.redis.lrange(key, start, end)

    def _lrem(self, key, value, count=0):
        if self.redis:
            self.redis.lrem(key, value, count)

    def set_p2p_product_detail(self, product):
        product_id = product.id
        product = serialize_instance(product)
        self._set('channel_p2p_product_detail_{0}'.format(product_id), json.dumps(product))

    def get_p2p_product_detail(self, product_id):
        p2p_product = self._get('channel_p2p_product_detail_{0}'.format(product_id))
        if p2p_product:
            p2p_product = json.loads(p2p_product)
            p2p_product = deserialize_instance(P2PProduct, p2p_product)

        return p2p_product
