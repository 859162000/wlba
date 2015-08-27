#!/usr/bin/env python
# encoding:utf-8

__author__ = 'zhanghe'

import logging
import json

from datetime import datetime
from marketing.models import IntroducedBy
from marketing.tops import Top
from marketing.utils import local_to_utc
from misc.views import MiscRecommendProduction

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.views.generic import TemplateView
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from wanglibao import settings
from wanglibao.templatetags.formatters import safe_phone_str
from wanglibao_account.models import UserPhoneBook
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_banner.models import AppActivate
from wanglibao_p2p.models import ProductAmortization, P2PEquity, P2PProduct, P2PRecord
from wanglibao_p2p.serializers import P2PProductSerializer
from wanglibao_rest.utils import split_ua, get_client_ip
from wanglibao_banner.models import Banner
from wanglibao_sms import messages as sms_messages
from wanglibao_sms.utils import send_validation_code
from wanglibao_sms.tasks import send_messages
from wanglibao_anti.anti.anti import AntiForAllClient
from wanglibao_account.forms import verify_captcha

logger = logging.getLogger(__name__)

class AppActivateImageAPIView(APIView):
    """ app端查询启动活动图片 """

    permission_classes = ()

    SIZE_MAP = {'1': 'img_one', '2': 'img_two', '3': 'img_three', '4': 'img_four'}
    DEVICE_MAP = {'ios': 'app_iso', 'android': 'app_android', 'act_iso': 'act_iso', 'act_android': 'act_android'}

    def post(self, request):
        size = request.DATA.get('size', '').strip()

        device = split_ua(request)
        device_type = device['device_type']

        if not device_type or not size:
            return Response({'ret_code': 20001, 'message': u'信息输入不完整'})

        if device_type not in ('ios', 'android') or int(size) not in (x for x in range(1, 9)):
            return Response({'ret_code': 20002, 'message': u'参数不合法'})

        if int(size) in (x for x in range(5, 9)):
            size = str(int(size) - 4)
            if device_type == 'ios': device_type = 'act_iso'
            if device_type == 'android': device_type = 'act_android'

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

                return Response({'ret_code': 0, 'message': 'ok', 'amount': float(amount), 'income_num': float(income_num)})

            else:
                # 未登陆用户 查询当月还款金额和当月还款项目
                start = datetime(now.year, now.month, 1)
                start_utc = local_to_utc(start, 'min')

                ams = ProductAmortization.objects.filter(settlement_time__range=(start_utc, timezone.now()), settled=True)
                for x in ams:
                    amount += x.principal + x.interest + x.penal_interest
                return Response({'ret_code': 0, 'message': 'ok', 'amount': float(amount), 'income_num': len(ams)})
        except Exception, e:
            logger.error(e.message)
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
    template_name = 'secure.jade'

class AppGuideView(TemplateView):
    """ app新手引导页面 """
    template_name = 'guide.jade'

class AppSecureView(TemplateView):
    """ app安全保障页面"""
    template_name = ''

class AppExploreView(TemplateView):
    """ app发现页面 """
    template_name = 'discover.jade'

    def get_context_data(self, **kwargs):
        #banner = Banner.objects.filter(device='mobile', type='banner', is_used=True).order_by('-priority')
        banner = Banner.objects.filter(Q(device='mobile'), Q(is_used=True), Q(is_long_used=True) | (Q(is_long_used=False) & Q(start_at__lte=timezone.now()) & Q(end_at__gte=timezone.now()))).order_by('-priority')
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

        manual = u"FIELD({column}, '正在招标', '满标待审核', '满标已审核', '满标待打款', '满标已打款','还款中')".format(column='status')

        if pager:
            return qs.filter(hide=False).filter(status__in=[
                u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标'
            ]).exclude(Q(category=u'票据') | Q(category=u'酒仙众筹标')).filter(pager).extra(select={'manual': manual}, order_by=['manual', '-priority', '-publish_time'])
        else:
            return qs.filter(hide=False).filter(status__in=[
                u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标'
            ]).exclude(Q(category=u'票据') | Q(category=u'酒仙众筹标')).extra(select={'manual': manual}, order_by=['manual', '-priority', '-publish_time'])


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

        # 主推标
        recommend_product_id = None
        if self.request.user and self.request.user.is_authenticated():
            user = self.request.user
            product_new = P2PProduct.objects.filter(hide=False, status=u'正在招标', category=u'新手标')
            if product_new.exists():
                if not P2PRecord.objects.filter(user=user).exists():
                    # 不存在购买记录
                    id_rate = [{'id': q.id, 'rate': q.completion_rate} for q in product_new]
                    id_rate = sorted(id_rate, key=lambda x: x['rate'], reverse=True)
                    recommend_product_id = id_rate[0]['id']
                else:
                    # 存在购买记录
                    misc = MiscRecommendProduction()
                    recommend_product_id = misc.get_recommend_product_except_new()

        if not recommend_product_id:
            misc = MiscRecommendProduction()
            recommend_product_id = misc.get_recommend_product_id()

        return qs.filter(id=recommend_product_id)


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


class SendValidationCodeView(APIView):
    """ app端获取验证码，不在设置状态码， """
    permission_classes = ()

    def post(self, request, phone):
        """
            modified by: Yihen@20150813
            descrpition: if(line299~line304)的修改，app端增加图片校验码验证
        """
        phone_number = phone.strip()
        if not AntiForAllClient(request).anti_special_channel():
            res, message = False, u"请输入验证码"
        else:
            res, message = verify_captcha(request.POST)
        if not res:
            return Response({"ret_code": 40044, "message": message})

        status, message = send_validation_code(phone_number, ip=get_client_ip(request))
        if status != 200:
            return Response({"ret_code": 30044, "message": message})

        return Response({"ret_code": 0, "message": u'验证码发送成功'})


class AppIncomeMiscTemplateView(TemplateView):
    """ 设置收益比例参数"""
    template_name = "app_income_misc.jade"

    def get_context_data(self, **kwargs):
        data = {'rate_wlb': 100, 'rate_p2p': 80, 'rate_fund': 60, 'rate_bank': 40}
        m = MiscRecommendProduction(key=MiscRecommendProduction.KEY_INCOME_DATA, desc=MiscRecommendProduction.DESC_INCOME_DATA, data=data)
        return {'income': m.get_recommend_products()}

    def post(self, request, **kwargs):
        rate_wlb = request.POST.get('rate_wlb', '')
        rate_p2p = request.POST.get('rate_p2p', '')
        rate_fund = request.POST.get('rate_fund', '')
        rate_bank = request.POST.get('rate_bank', '')
        if not rate_wlb or not rate_p2p or not rate_fund or not rate_bank:
            messages.warning(request, u'输入数据不合法')
            return redirect('./income_misc')

        data = {'rate_wlb': rate_wlb, 'rate_p2p': rate_p2p, 'rate_fund': rate_fund, 'rate_bank': rate_bank}
        try:
            m = MiscRecommendProduction(key=MiscRecommendProduction.KEY_INCOME_DATA)
            m.update_value(value=data)
            messages.warning(request, u'数据新增(修改)成功')
            return redirect('./income_misc')
        except:
            messages.warning(request, u'系统错误，请联系开发人员')
            return redirect('./income_misc')


class AppIncomeRateAPIView(APIView):
    """ 查询获取收益比例配置信息 """
    permission_classes = ()

    def post(self, request):
        try:
            m = MiscRecommendProduction(key=MiscRecommendProduction.KEY_INCOME_DATA)
            rate = m.get_recommend_products()
            if rate:
                return Response({'ret_code': 0, 'message': '成功', 'rate': rate})
            else:
                return Response({'ret_code': 20001, 'message': u'请联系管理员配置收益比例数据'})
        except Exception, e:
            logger.error(e.message)
            return Response({'ret_code': 20002, 'message': 'fail'})


class AppPhoneBookUploadAPIView(APIView):
    """ user uploading phone book """
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user

        phones = request.DATA.get('phones', '')
        if not phones:
            return Response({'ret_code': 20001, 'message': u'数据输入不合法'})
        phones = json.loads(phones)
        try:
            UserPhoneBook.objects.filter(user=user).exclude(phone__in=phones.keys()).update(is_used=False)
            phone_db = [u.get('phone') for u in UserPhoneBook.objects.filter(user=user, phone__in=phones.keys()).values('phone')]

            phone_new_list = []
            for p in phones.keys():
                if p in phone_db:
                    UserPhoneBook.objects.filter(user=user, phone=p).update(name=phones.get(p), is_used=True)
                else:
                    phone_book = UserPhoneBook()
                    phone_book.user = user
                    phone_book.phone = p
                    phone_book.name = phones.get(p)
                    if User.objects.filter(wanglibaouserprofile__phone=p).exists():
                        phone_book.is_register = True
                    else:
                        phone_book.is_register = False

                    if IntroducedBy.objects.filter(introduced_by=user, user__wanglibaouserprofile__phone=p).exists():
                        phone_book.is_invite = True
                    else:
                        phone_book.is_invite = False

                    phone_book.is_used = True
                    phone_new_list.append(phone_book)
            if phone_new_list:
                UserPhoneBook.objects.bulk_create(phone_new_list)
            return Response({'ret_code': 0, 'message': 'success'})
        except Exception, e:
            logger.error(e.message)
            return Response({'ret_code': 20002, 'message': u'同步通讯录错误'})


class AppPhoneBookQueryAPIView(APIView):
    """ 查询未邀请好友，即用户未注册 """
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        phone_book = UserPhoneBook.objects.filter(user=request.user, is_used=True, is_register=False)

        books = register_list = list()
        for book in phone_book:
            if User.objects.filter(wanglibaouserprofile__phone=book.phone).exists():
                register_list.append(book.phone)
            else:
                books.append({
                    'name': book.name,
                    'phone': book.phone,
                    'status': True if book.invite_at and book.invite_at > local_to_utc(datetime.now(), 'min') else False,
                    }
                )

        if register_list:
            UserPhoneBook.objects.filter(user=request.user, phone__in=register_list).update(is_register=True)

        return Response({'ret_code': 0, 'message': 'success', 'books': books})


class AppPhoneBookAlertApiView(APIView):
    """ 邀请注册和提醒投资接口
    flag:   1 invite user to register
            2 alert user to invest
    """
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        flag = request.DATA.get('flag')
        phone = request.DATA.get('phone')
        if not phone or not flag or (flag and int(flag) not in(1, 2)):
            return Response({'ret_code': 20001, 'message': u'数据输入不合法'})

        try:
            user_book = UserPhoneBook.objects.filter(user=user, is_used=True, phone=phone).first()
            if not user_book:
                return Response({'ret_code': 20002, 'message': u'被提醒用户不存在'})

            profile = user.wanglibaouserprofile
            send_name = profile.name if profile.id_is_valid else safe_phone_str(profile.phone)
            # 投资提醒
            if int(flag) == 1:
                if not (user_book.alert_at and user_book.alert_at > local_to_utc(datetime.now(), 'min')):
                    self._send_sms(phone, sms_messages.sms_alert_invest(name=send_name))
                    user_book.alert_at = timezone.now()
                    user_book.save()
            # 邀请提醒
            elif int(flag) == 2:
                if User.objects.filter(wanglibaouserprofile__phone=phone).exists():
                    user_book.is_register = True
                    if IntroducedBy.objects.filter(introduced_by=user, user_wanglibaouserprofile__phone=phone).exists():
                        user_book.is_invite = True
                    user_book.save()

                if not user_book.is_register and not (user_book.invite_at and user_book.invite_at > local_to_utc(datetime.now(), 'min')):
                    self._send_sms(phone, sms_messages.sms_alert_invite(name=send_name, phone=profile.phone))
                    user_book.invite_at = timezone.now()
                    user_book.save()

            return Response({'ret_code': 0, 'message': 'ok'})
        except Exception, e:
            logger.error(e.message)
            return Response({'ret_code': 20003, 'message': u'内部程序错误'})

    def _send_sms(self, phone, sms):
        send_messages.apply_async(kwargs={
            'phones': [phone],
            'messages': [sms]
        })
