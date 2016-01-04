# encoding:utf-8
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context
from django.utils import timezone
from django.views.generic import TemplateView
from misc.views import MiscRecommendProduction
from wanglibao_p2p.models import P2PProduct, P2PRecord
from wanglibao_banner.models import Banner, Partner
from marketing.models import TimelySiteData
from marketing.utils import pc_data_generator
from wanglibao_p2p.models import P2PEquity
from wanglibao_buy.models import FundHoldInfo
from django.core.urlresolvers import reverse
import re
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import EnterpriseUserProfile, EnterpriseUserProfileExtra
from .forms import EnterpriseUserProfileForm

#
# class QiYeIndex(TemplateView):
#     template_name = 'qiye_login.jade'
#
#     PRODUCT_LENGTH = 3
#
#     def _period_3(self, p2p):
#         return p2p.filter(Q(pay_method__contains=u'日计息') & Q(period__gte=1) & Q(period__lt=90) | ~Q(pay_method__contains=u'日计息') & Q(period__gte=1) & Q(period__lt=3))
#
#     def _period_6(self, p2p):
#         return p2p.filter(Q(pay_method__contains=u'日计息') & (Q(period__gte=90) & Q(period__lt=180)) | ~Q(pay_method__contains=u'日计息') & (Q(period__gte=3) & Q(period__lt=6)))
#
#     def _period_9(self, p2p):
#         return p2p.filter(Q(pay_method__contains=u'日计息') & Q(period__gte=180) | ~Q(pay_method__contains=u'日计息') & Q(period__gte=6))
#
#     def _filter_product_period(self, p2p, period):
#         if period == 3:
#             p2p = self._period_3(p2p)
#         elif period == 6:
#             p2p = self._period_6(p2p)
#         elif period == 9:
#             p2p = self._period_9(p2p)
#
#         return p2p
#
#     def _full_product_payment(self, period, num, product_id=None, order_by='index'):
#         """ 查询满表且已经还款中的标 """
#         p2p = P2PProduct.objects.select_related(
#             'warrant_company', 'activity'
#         ).filter(
#             hide=False,
#             publish_time__lte=timezone.now(),
#             status=u'还款中'
#         )
#         if product_id:
#             p2p = p2p.exclude(id__in=product_id)
#
#         if order_by == 'index':
#             return self._filter_product_period(p2p, period).order_by('-soldout_time', '-priority')[:num]
#         else:
#             return self._filter_product_period(p2p, period).order_by('-expected_earning_rate', 'period')[:num]
#
#     def _full_product_nonpayment(self, period, num, product_id=None, order_by='index'):
#         """ 查询满表但是非还款中的标 """
#         p2p = P2PProduct.objects.select_related(
#             'warrant_company', 'activity'
#         ).filter(
#             hide=False,
#             publish_time__lte=timezone.now(),
#             status__in=[u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核']
#         )
#         if product_id:
#             p2p = p2p.exclude(id__in=product_id)
#         if order_by == 'index':
#             return self._filter_product_period(p2p, period).order_by('-soldout_time', '-priority')[:num]
#         else:
#             return self._filter_product_period(p2p, period).order_by('-expected_earning_rate', 'period')[:num]
#
#     def get_products(self, period, product_id=None, order_by='index'):
#         """ 查询符合条件的标列表
#         3:1-3个月（包含3月）
#         6:4-6个月（包含6个月）
#         9:6个月以上
#         """
#         if period not in (3, 6, 9):
#             return []
#         p2p_list = []
#         p2p = P2PProduct.objects.select_related(
#             'warrant_company', 'activity'
#         ).filter(
#             hide=False, publish_time__lte=timezone.now(), status=u'正在招标'
#         )
#
#         if product_id:
#             p2p = p2p.exclude(id__in=product_id)
#
#         if order_by == 'index':
#             p2p = self._filter_product_period(p2p, period).order_by('-priority', '-total_amount')[:self.PRODUCT_LENGTH]
#         else:
#             p2p = self._filter_product_period(p2p, period).order_by('-expected_earning_rate', 'period')[:self.PRODUCT_LENGTH]
#
#         p2p_list.extend(p2p)
#         # 使用满标但是未还款的扩充
#         if len(p2p_list) < self.PRODUCT_LENGTH:
#             p2p_list.extend(self._full_product_nonpayment(period=period,
#                                                           num=self.PRODUCT_LENGTH-len(p2p_list),
#                                                           product_id=product_id, order_by=order_by))
#         # 使用慢标且还款中的扩充
#         if len(p2p_list) < self.PRODUCT_LENGTH:
#             p2p_list.extend(self._full_product_payment(period=period,
#                                                        num=self.PRODUCT_LENGTH-len(p2p_list),
#                                                        product_id=product_id, order_by=order_by))
#         return p2p_list
#
#     def get_context_data(self, **kwargs):
#         # 需要过滤的标id
#         exclude_pid = list()
#
#         # 主推标
#         recommend_product_id = None
#         if self.request.user and self.request.user.is_authenticated():
#             user = self.request.user
#             product_new = P2PProduct.objects.filter(hide=False, publish_time__lte=timezone.now(),
#                                                     status=u'正在招标', category=u'新手标')
#             if product_new.exists():
#                 if not P2PRecord.objects.filter(user=user).exists():
#                     # 不存在购买记录
#                     id_rate = [{'id': q.id, 'rate': q.completion_rate} for q in product_new]
#                     id_rate = sorted(id_rate, key=lambda x: x['rate'], reverse=True)
#                     recommend_product_id = id_rate[0]['id']
#                 else:
#                     # 存在购买记录
#                     misc = MiscRecommendProduction()
#                     recommend_product_id = misc.get_recommend_product_except_new()
#                     # 将所有新手表过滤
#                     exclude_pid += [p.id for p in product_new]
#
#         if not recommend_product_id:
#             misc = MiscRecommendProduction()
#             recommend_product_id = misc.get_recommend_product_id()
#
#         recommend_product = P2PProduct.objects.filter(id=recommend_product_id)
#
#         exclude_pid.append(recommend_product_id)
#         exclude_pid = list(set(exclude_pid))
#
#         # p2p_products = []
#         # 获取期限小于等于3个月的标，天数为90天(period<=3 or period<=90)
#         p2p_lt3 = self.get_products(period=3, product_id=exclude_pid)
#         # 获取期限大雨3个月小于等于6个月的标，天数为180天(3<period<=6 or 90<period<=180)
#         p2p_lt6 = self.get_products(period=6, product_id=exclude_pid)
#         # 获取期限大于6个月的标(period>6 or period>180)
#         p2p_gt6 = self.get_products(period=9, product_id=exclude_pid)
#         getmore = True
#
#         banners = Banner.objects.filter(Q(device=Banner.PC_2), Q(is_used=True), Q(is_long_used=True) | (Q(is_long_used=False) & Q(start_at__lte=timezone.now()) & Q(end_at__gte=timezone.now())))
#
#
#         # 网站数据
#         m = MiscRecommendProduction(key=MiscRecommendProduction.KEY_PC_DATA, desc=MiscRecommendProduction.DESC_PC_DATA)
#         site_data = m.get_recommend_products()
#         if site_data:
#             site_data = site_data[MiscRecommendProduction.KEY_PC_DATA]
#         else:
#             site_data = pc_data_generator()
#             m.update_value(value={MiscRecommendProduction.KEY_PC_DATA: site_data})
#             # m.update_value(value=site_data)
#
#         site_data['updated_at'] = m.get_misc().updated_at
#
#         # 合作伙伴
#         partners_data = Partner.objects.filter(type='partner')
#         partners = [
#             {'name': partner.name, 'link': partner.link, 'image': partner.image}
#             for partner in partners_data
#         ]
#
#         # 总资产
#         p2p_total_asset = 0
#         fund_total_asset = 0
#         if self.request.user and self.request.user.is_authenticated():
#             user = self.request.user
#             p2p_equities = P2PEquity.objects.filter(user=user, confirm=True).filter(product__status__in=[
#                 u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
#             ]).select_related('product')
#
#             unpayed_principle = 0
#             for equity in p2p_equities:
#                 unpayed_principle += equity.unpaid_principal
#             p2p_total_asset = user.margin.margin + user.margin.freeze + user.margin.withdrawing + unpayed_principle
#
#             fund_hold_info = FundHoldInfo.objects.filter(user__exact=user)
#             if fund_hold_info.exists():
#                 for hold_info in fund_hold_info:
#                     fund_total_asset += hold_info.current_remain_share + hold_info.unpaid_income
#
#         return {
#             "recommend_product": recommend_product,
#             "p2p_lt_three": p2p_lt3,
#             "p2p_lt_six": p2p_lt6,
#             "p2p_gt_six": p2p_gt6,
#             'banners': banners,
#             'site_data': site_data,
#             'getmore': getmore,
#             'partners': partners,
#             'p2p_total_asset': float(p2p_total_asset + fund_total_asset)
#         }
#
#     def get(self, request, *args, **kwargs):
#         device_list = ['android', 'iphone']
#         user_agent = request.META.get('HTTP_USER_AGENT', "").lower()
#         for device in device_list:
#             match = re.search(device, user_agent)
#             if match and match.group():
#                 return HttpResponseRedirect(reverse('weixin_p2p_list'))
#
#         return super(QiYeIndex, self).get(request, *args, **kwargs)


class QiYeIndex(TemplateView):
    template_name = 'info.jade'


class GetRequestUserType(APIView):
    """获取认证用户的用户类型"""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        json_response = {
            'data': request.user.wanglibaouserprofile.utype,
            'message': 'ok'
        }

        return HttpResponse(json.dumps(json_response), content_type='application/json')


class EnterpriseUserProfileExtraApi(APIView):
    """企业用户认证扩展资料接收接口"""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        field_name = request.POST.get('field_name')
        e_profile, created = EnterpriseUserProfileExtra.objects.get_or_create(user=user)
        if field_name == 'business_license':
            business_license = request.POST.get('business_license')
            # FixMe, 添加图片校验
            if business_license:
                e_profile.business_license = business_license
                e_profile.save()
                response_data = {
                    'message': 'ok',
                    'ret_code': 10000,
                }
            else:
                response_data = {
                    'message': u'请选择营业执照',
                    'ret_code': 10001,
                }
        elif field_name == 'registration_cert':
            registration_cert = request.POST.get('registration_cert')
            # FixMe, 添加图片校验
            if registration_cert:
                e_profile.registration_cert = registration_cert
                e_profile.save()
                response_data = {
                    'message': 'ok',
                    'ret_code': 10000,
                }
            else:
                response_data = {
                    'message': u'请选择税务登记证',
                    'ret_code': 10001,
                }
        else:
            response_data = {
                'message': 'unknow error',
                'ret_code': 50001,
            }

        return HttpResponse(json.dumps(response_data), content_type='application/json')


class GetEnterpriseUserProfileApi(APIView):
    """企业用户认证资料获取接口"""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        try:
            e_profile = EnterpriseUserProfile.objects.get(user=user)
        except EnterpriseUserProfile.DoesNotExist:
            e_profile = None

        try:
            e_profile_extra = EnterpriseUserProfileExtra.objects.get(user=user)
        except EnterpriseUserProfileExtra.DoesNotExist:
            e_profile_extra = None

        return {
            'profile': e_profile,
            'extra': e_profile_extra,
            'ret_code': 10000
        }


class EnterpriseUserProfileApi(APIView):
    """企业用户认证资料接收接口"""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        form = EnterpriseUserProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            e_profile = EnterpriseUserProfile.objects.get(user=user)
            if e_profile:
                response_data = {
                    'message': 'user[%s] enterprise profile has been exists',
                    'ret_code': 10001,
                }
                return HttpResponse(json.dumps(response_data), content_type='application/json')

            e_profile = EnterpriseUserProfile()
            e_profile.user = user
            e_profile.company_name = form.cleaned_data['company_name']
            e_profile.business_license = form.cleaned_data['business_license']
            e_profile.registration_cert = form.cleaned_data['registration_cert']
            e_profile.certigier_name = form.cleaned_data['certigier_name']
            e_profile.certigier_phone = form.cleaned_data['certigier_phone']
            e_profile.company_address = form.cleaned_data['company_address']
            e_profile.company_account = form.cleaned_data['company_account']
            e_profile.company_account_name = form.cleaned_data['company_account_name']
            e_profile.deposit_bank_province = form.cleaned_data['deposit_bank_province']
            e_profile.deposit_bank_city = form.cleaned_data['deposit_bank_city']
            e_profile.bank_branch_address = form.cleaned_data['bank_branch_address']

