# encoding:utf-8

import pickle
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
from wanglibao_p2p.models import P2PProduct
from wanglibao_redis.backend import redis_backend


def cache_generate_detail():

    cache_backend = redis_backend()
    p2p_products = P2PProduct.objects.select_related('activity')\
        .exclude(status=u'流标').exclude(status=u'录标').exclude(status=u'正在招标').filter(hide=False).all()

    for p2p in p2p_products:
        # 先删除key，再缓存，避免重复
        cache_backend.redis.delete('p2p_detail_{0}'.format(p2p.id))

        p2p_detail = cache_backend.get_cache_p2p_detail(p2p.id)

        if p2p.status != u'正在招标':
            cache_backend.redis.set('p2p_detail_{0}'.format(p2p.id), pickle.dumps(p2p_detail))

    return True


def cache_generate_list():
    cache_backend = redis_backend()

    p2p_products = P2PProduct.objects.select_related('warrant_company', 'activity').filter(hide=False).filter(
        Q(publish_time__lte=timezone.now())).filter(status__in=[
            u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中'
        ]).order_by('soldout_time')

    for p2p in p2p_products:
        cache_backend.push_p2p_products(p2p)

    return True


if __name__ == "__main__":
    cache_generate_detail()
    cache_generate_list()