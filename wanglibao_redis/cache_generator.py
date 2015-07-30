# encoding:utf-8

import pickle
from django.utils import timezone
from django.db.models import Q
from django.forms import model_to_dict
from decimal import Decimal
from wanglibao_p2p.models import P2PProduct
from wanglibao_redis.backend import redis_backend
from wanglibao_announcement.models import Announcement
from marketing.models import NewsAndReport
from wanglibao_banner.models import Banner


cache_backend = redis_backend()

def cache_generate_detail():
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
    p2p_products = P2PProduct.objects.select_related('warrant_company', 'activity').filter(hide=False).filter(
        Q(publish_time__lte=timezone.now())).filter(status__in=[
            u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中'
        ]).order_by('soldout_time')

    for p2p in p2p_products:
        cache_backend.push_p2p_products(p2p)

    return True

#缓存公告
def cache_announcement():
    cache_backend._delete("announcement")

    annos = Announcement.objects.filter(Q(type='all') | Q(type='homepage')).filter(status=1).order_by('-priority', '-createtime')
    if annos:
        annos = annos[:10]
    result = []
    for x in annos:
        if not x.hideinlist:
            result.append(model_to_dict(x))

    cache_backend._set("announcement", pickle.dumps(result))

#缓存新闻
def cache_news():
    cache_backend._delete("announcement_news")
    news = NewsAndReport.objects.all().order_by("-score")[:5]
    result = []
    for x in news:
        result.append(model_to_dict(x))

    cache_backend._set("announcement_news", pickle.dumps(result))

#缓存banner
def cache_banners():
    cache_backend._delete("banners")
    banners = Banner.objects.filter(Q(device=Banner.PC_2), Q(is_used=True), Q(is_long_used=True) | Q(is_long_used=False))
    result = []
    for x in banners:
        if x.start_at and x.end_at:
            result.append(model_to_dict(x))

    cache_backend._set("banners", pickle.dumps(result))

if __name__ == "__main__":
    cache_generate_detail()
    cache_generate_list()
    cache_announcement()
    cache_news()
    cache_banners()
