# encoding:utf-8
import pickle
from wanglibao_redis.backend import redis_backend
from wanglibao_p2p.models import P2PProduct
from django.db.models import Q
from django.utils import timezone

# Add by hb on 2015-12-08 : rename "get_p2p_list" to "get_p2p_list_slow", and add new "get_p2p_list"
def get_p2p_list_slow():

    cache_backend = redis_backend()

    p2p_done = P2PProduct.objects.select_related('warrant_company', 'activity').filter(hide=False).filter(
        Q(publish_time__lte=timezone.now())) \
        .filter(status=u'正在招标').order_by('-publish_time')

    p2p_done_list = cache_backend.get_p2p_list_from_objects(p2p_done)

    p2p_full_list, p2p_repayment_list, p2p_finished_list = [], [], []

    if cache_backend._is_available() and cache_backend._exists('p2p_products_full'):
        p2p_full_cache = cache_backend._lrange('p2p_products_full', 0, -1)
        for product in p2p_full_cache:
            p2p_full_list.extend([pickle.loads(product)])
    else:
        p2p_full = P2PProduct.objects.select_related('warrant_company', 'activity') \
            .filter(hide=False).filter(Q(publish_time__lte=timezone.now())) \
            .filter(status__in=[u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核']) \
            .order_by('-soldout_time', '-priority')
        p2p_full_list = cache_backend.get_p2p_list_from_objects(p2p_full)

    if cache_backend._is_available() and cache_backend._exists('p2p_products_repayment'):
        p2p_repayment_cache = cache_backend._lrange('p2p_products_repayment', 0, -1)

        for product in p2p_repayment_cache:
            p2p_repayment_list.extend([pickle.loads(product)])
    else:
        p2p_repayment = P2PProduct.objects.select_related('warrant_company', 'activity') \
            .filter(hide=False).filter(Q(publish_time__lte=timezone.now())) \
            .filter(status=u'还款中').order_by('-soldout_time', '-priority')

        p2p_repayment_list = cache_backend.get_p2p_list_from_objects(p2p_repayment)

    if cache_backend._is_available() and cache_backend._exists('p2p_products_finished'):
        p2p_finished_cache = cache_backend._lrange('p2p_products_finished', 0, -1)

        for product in p2p_finished_cache:
            p2p_finished_list.extend([pickle.loads(product)])
    else:
        p2p_finished = P2PProduct.objects.select_related('warrant_company', 'activity') \
            .filter(hide=False).filter(Q(publish_time__lte=timezone.now())) \
            .filter(status=u'已完成').order_by('-soldout_time', '-priority')

        p2p_finished_list = cache_backend.get_p2p_list_from_objects(p2p_finished)

    return p2p_done_list, p2p_full_list, p2p_repayment_list, p2p_finished_list

def get_p2p_list():

    cache_backend = redis_backend()

    p2p_all = P2PProduct.objects.select_related('warrant_company', 'activity__rule') \
        .filter(hide=False).filter(Q(status_int__gte=6)).filter(Q(publish_time__lte=timezone.now())) \
        .order_by('-status_int', '-publish_time', '-soldout_time', '-priority')

    p2p_done_list = cache_backend.get_p2p_list_from_objects_by_status(p2p_all, 9)
    p2p_full_list = cache_backend.get_p2p_list_from_objects_by_status(p2p_all, 8)
    p2p_repayment_list = cache_backend.get_p2p_list_from_objects_by_status(p2p_all, 7)
    p2p_finished_list = cache_backend.get_p2p_list_from_objects_by_status(p2p_all, 6)

    return p2p_done_list, p2p_full_list, p2p_repayment_list, p2p_finished_list

