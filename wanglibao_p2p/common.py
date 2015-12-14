# encoding:utf-8
from wanglibao_redis.backend import redis_backend
from wanglibao_p2p.models import P2PProduct
from django.db.models import Q
from django.utils import timezone

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
