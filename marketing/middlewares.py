# encoding:utf-8
from django.conf import settings
import urlparse
from wanglibao_account.cooperation import CoopRegister
import logging

logger = logging.getLogger("marketing")

class PromotionTokenMiddleWare(object):
    def process_request(self, request):
        token = request.GET.get(settings.PROMO_TOKEN_QUERY_STRING, None)
        if token:
            request.session[settings.PROMO_TOKEN_QUERY_STRING] = token
        CoopRegister(request).all_processors_for_session()

class StatsKeyWordMiddleWare(object):
    def __init__(self):
        self.statics ={
            'www.baidu.com': {
                'website': 'www.baidu.com',
                'name': u'百度网站',
                'keyword': 'wd',
            },
            'm.baidu.com': {
                'website': 'm.baidu.com',
                'name': u'百度移动站',
                'keyword': 'word',
            },
            'www.haosou.com': {
                'website': 'www.haosou.com',
                'name': u'360搜索',
                'keyword': 'q'
            },
            'www.sogou.com': {
                'website': 'www.sogou.com',
                'name': u'搜狗页面搜索',
                'keyword': 'query'
            },
            'wap.sogou.com': {
                'website': 'wap.sogou.com',
                'name': u'搜狗移动站',
                'keyword': 'keyword'
            },
            'm.sp.sm.cn': {
                'website': 'm.sp.sm.sn',
                'name': u'神马搜索',
                'keyword': 'q'
            },
            'www.youdao.com': {
                'website': 'www.youdao.com',
                'name': u'有道搜索',
                'keyword': 'q'
            },
            'cn.bing.com': {
                'website': 'cn.bing.com',
                'name': u'必应',
                'keyword': 'q'
            },

        }

    def process_request(self, request):
        referer = request.META.get("HTTP_REFERER", "")
        if referer:
            res = urlparse.urlparse(referer)
            website = filter(lambda item: item in res.netloc, self.statics.keys())
            if website:
                website = website[0]
                qs = urlparse.parse_qs(res.query)
                if self.statics[website]['keyword'] in qs:
                    request.session["promo_source_keyword"] = "|".join(qs[self.statics[website]['keyword']])
                    request.session["promo_source_site_name"] = self.statics[website]['name']
                    request.session['promo_source_website'] = self.statics[website]['website']
                    #if settings.DEBUG:
                    #    logger.debug("keyword:%s, site_name:%s, website:%s" % (request.session.get("promo_source_keyword"),
                    #                                                       request.session.get("promo_source_site_name"),
                    #                                                       request.session.get("promo_source_website")
                    #                                                       ))
