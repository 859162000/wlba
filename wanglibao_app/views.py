#!/usr/bin/env python
# encoding:utf-8

__author__ = 'zhanghe'

import logging
import json

from datetime import datetime
from marketing.tops import Top
from marketing.utils import local_to_utc
from misc.views import MiscRecommendProduction

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.views.generic import TemplateView
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from wanglibao import settings
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_banner.models import AppActivate
from wanglibao_p2p.models import ProductAmortization, P2PEquity, P2PProduct
from wanglibao_p2p.serializers import P2PProductSerializer
from wanglibao_rest.utils import split_ua
from wanglibao_banner.models import Banner



class AppActivateImageAPIView(APIView):
    """ app端查询启动活动图片 """

    permission_classes = ()

    SIZE_MAP = {'1': 'img_one', '2': 'img_two', '3': 'img_three', '4': 'img_four'}
    DEVICE_MAP = {'ios': 'app_iso', 'android': 'app_android'}

    def post(self, request):
        size = request.DATA.get('size', '').strip()

        device = split_ua(request)
        device_type = device['device_type']

        if not device_type or not size:
            return Response({'ret_code': 20001, 'message': u'信息输入不完整'})

        if device_type not in ('ios', 'android') or size not in ('1', '2', '3'):
            return Response({'ret_code': 20002, 'message': u'参数不合法'})

        size = self.SIZE_MAP[size]

        activate = AppActivate.objects.filter(Q(is_used=True), Q(device=self.DEVICE_MAP[device_type]), Q(is_long_used=True) | (Q(is_long_used=False) & Q(start_at__lte=timezone.now()) & Q(end_at__gte=timezone.now()))).first()
        if activate:
            if size == 'img_one':
                img_url = activate.img_one
            elif size == 'img_two':
                img_url = activate.img_two
            elif size == 'img_three':
                img_url = activate.img_three
            elif size == 'img_four':
                img_url = activate.img_four
            else:
                img_url = ''

            if img_url:
                img_url = '{host}/media/{url}'.format(host=settings.CALLBACK_HOST, url=img_url)
                # img_url = '{host}/media/{url}'.format(host='http://192.168.1.116:8000', url=img_url)
                return Response({'ret_code': 0, 'message': 'ok', 'image': img_url})

        return Response({'ret_code': 20003, 'message': 'fail'})


class AppRepaymentAPIView(APIView):
    """ app 首页当月还款和用户收益接口 """

    permission_classes = ()

    def post(self, request):
        now = datetime.now()
        amount, income_num = 0, 0
        try:
            if request.user and request.user.is_authenticated():
                # 登陆用户 查询当天收益和累计收益
                user = request.user
                start_utc = local_to_utc(now, 'min')

                p2p_equities = P2PEquity.objects.filter(user=user, confirm=True, product__status__in=[
                    u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
                ]).select_related('product')
                for equity in p2p_equities:
                    amount += equity.pre_paid_interest  # 累积收益
                    amount += equity.activity_interest  # 活动收益
                    if equity.confirm_at >= start_utc:
                        income_num += equity.pre_paid_interest
                        income_num += equity.activity_interest

                return Response({'ret_code': 0, 'message': 'ok', 'amount': amount, 'income_num': income_num})

            else:
                # 未登陆用户 查询当月还款金额和当月还款项目
                start = datetime(now.year, now.month, 1)
                start_utc = local_to_utc(start, 'min')

                ams = ProductAmortization.objects.filter(settlement_time__range=(start_utc, timezone.now()), settled=True)
                for x in ams:
                    amount += x.principal + x.interest + x.penal_interest
                return Response({'ret_code': 0, 'message': 'ok', 'amount': amount, 'income_num': len(ams)})
        except Exception, e:
            logging.error(e.message)
            return Response({'ret_code': 20001, 'message': 'fail'})


class AppDayListView(TemplateView):
    """ app端榜单 """
    template_name = 'day-list.jade'

    def get_context_data(self, **kwargs):

        top = Top(limit=10)
        top_list = top.day_tops_activate(day=datetime.now(), amount_min=0)
        return {
            'top_list': top_list,
        }


class AppGuardView(TemplateView):
    """ app保障页面 """
    template_name = ''

    def get_context_data(self, **kwargs):
        return {}

class AppGuideView(TemplateView):
    """ app新手引导页面 """
    template_name = 'guide.jade'

    def get_context_data(self, **kwargs):
        return {}

class AppSecureView(TemplateView):
    """ app安全保障页面"""
    template_name = 'secure.jade'

    def get_context_data(self, **kwargs):
        return {}

class AppExploreView(TemplateView):
    """ app发现页面 """
    template_name = 'discover.jade'

    def get_context_data(self, **kwargs):
        banner = Banner.objects.filter(device='weixin', type='banner', is_used=True).order_by('-priority')
        return {
            'banner': banner,
        }


class AppP2PProductViewSet(PaginatedModelViewSet):
    """ app查询标列表接口 """

    model = P2PProduct
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = P2PProductSerializer
    paginate_by = 10

    def get_queryset(self):
        qs = super(AppP2PProductViewSet, self).get_queryset()

        maxid = self.request.QUERY_PARAMS.get('maxid', '')
        minid = self.request.QUERY_PARAMS.get('minid', '')

        pager = None
        if maxid and not minid:
            pager = Q(id__gt=maxid)
        if minid and not maxid:
            pager = Q(id__lt=minid)

        if pager:
            return qs.filter(hide=False).filter(status__in=[
                u'满标已审核', u'还款中', u'正在招标'
            ]).exclude(Q(category=u'票据') | Q(category=u'酒仙众筹标')).filter(pager).order_by('-priority', '-publish_time')
        else:
            return qs.filter(hide=False).filter(status__in=[
                u'满标已审核', u'还款中', u'正在招标'
            ]).exclude(Q(category=u'票据') | Q(category=u'酒仙众筹标')).order_by('-priority', '-publish_time')


class AppRecommendViewSet(PaginatedModelViewSet):
    """ app查询主推标接口
    如果设置了主推标，按照设置的顺序显示
    如果没有设置主推标，那就查找最近一个将要买完的显示
    """
    model = P2PProduct
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = P2PProductSerializer
    paginate_by = 1

    def get_queryset(self):
        qs = super(AppRecommendViewSet, self).get_queryset()

        misc = MiscRecommendProduction()
        ids = misc.get_recommend_products()
        if ids:
            for id in ids:
                recommend = qs.filter(hide=False, status=u'正在招标', id=id)
                if recommend:
                    return recommend
        # 自定义查询标
        productions = qs.filter(hide=False, status=u'正在招标').exclude(Q(category=u'票据') | Q(category=u'酒仙众筹标'))
        if productions:
            id_rate = [{'id': q.id, 'rate': q.completion_rate} for q in productions]
            id_rate = sorted(id_rate, key=lambda x: x['rate'], reverse=True)
            return qs.filter(id=id_rate[0]['id'])

        else:
            return qs.filter(hide=False).exclude(Q(category=u'票据') | Q(category=u'酒仙众筹标')).order_by('-priority', '-publish_time')


class RecommendProductManagerView(TemplateView):
    """ 推荐标的管理 """
    template_name = 'recommend_production.jade'

    def _get_product(self, id):
        if isinstance(id, list):
            return P2PProduct.objects.filter(id__in=id).order_by('-id')
        else:
            return P2PProduct.objects.filter(id=id).order_by('-id')

    def get_context_data(self, **kwargs):
        p2p_list = []
        misc = MiscRecommendProduction()
        ids = misc.get_recommend_products()
        if ids:
            products = P2PProduct.objects.filter(id__in=ids)
            for product in products:
                p2p_list.append({
                    'id': product.id,
                    'name': product.name,
                    'total_amount': product.total_amount,
                })

            p2p_list = sorted(p2p_list, key=lambda x: ids.index(x['id']))

        return {'p2p_list': p2p_list}

    def post(self, request, **kwargs):
        """ 添加删除 """
        operate = request.POST.get('manager')
        product_id = request.POST.get('product_id')
        if not operate or not product_id:
            messages.warning(request, u'请填写标的id')
            return redirect('./recommend_manager')

        if product_id and not product_id.isdigit():
            messages.warning(request, u'标的id不合法')
            return redirect('./recommend_manager')

        try:
            product_id = int(product_id)
            misc = MiscRecommendProduction()
            ids = misc.get_recommend_products()

            product = self._get_product(product_id)
            if not product:
                messages.warning(request, u'不存在id对应的标')
                return redirect('./recommend_manager')

            if operate == 'add':
                if product_id in ids:
                    messages.warning(request, u'此标已经被设置，不允许重复设置')
                    return redirect('./recommend_manager')

                if misc.add_product(product_id=product_id):
                    messages.warning(request, u'增加成功')
                    return redirect('./recommend_manager')

                messages.warning(request, u'增加失败')
                return redirect('./recommend_manager')

            elif operate == 'del':
                if product_id not in ids:
                    messages.warning(request, u'此标未被设置')
                    return redirect('./recommend_manager')

                if misc.del_product(product_id=product_id):
                    messages.warning(request, u'删除成功')
                    return redirect('./recommend_manager')

                messages.warning(request, u'删除失败')
                return redirect('./recommend_manager')

            return redirect('./recommend_manager')
        except Exception, e:
            logging.error(e.message)
            return redirect('./recommend_manager')
>>>>>>> e34c61fd5adef7206c138372c7a1ac021aebe6e3
