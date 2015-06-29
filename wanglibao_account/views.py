# encoding: utf-8
import datetime
import logging
import json
import math
import hashlib
import urllib
import urlparse

from decimal import Decimal
from django.contrib import auth
from django.contrib.auth import login as auth_login
from django.db.models import Sum, Q
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from django.core.urlresolvers import reverse
from django.core import serializers
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed, Http404, HttpResponseRedirect
from django.shortcuts import resolve_url, render_to_response
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, View
from registration.views import RegistrationView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from forms import EmailOrPhoneRegisterForm, ResetPasswordGetIdentifierForm, IdVerificationForm
from marketing.models import IntroducedBy, Reward, RewardRecord
from marketing.utils import set_promo_user
from marketing import tools
from shumi_backend.exception import FetchException, AccessException
from shumi_backend.fetch import UserInfoFetcher
from wanglibao_account.utils import detect_identifier_type, create_user, generate_contract
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_account import third_login, backends as account_backends, message as inside_message
from wanglibao_account.forms import EmailOrPhoneAuthenticationForm
from wanglibao_account.serializers import UserSerializer
from wanglibao_buy.models import TradeHistory, BindBank, FundHoldInfo, DailyIncome
from wanglibao_p2p.models import P2PRecord, P2PEquity, ProductAmortization, UserAmortization, Earning, \
    AmortizationRecord, P2PProductContract, P2PProduct, P2PEquityJiuxian, AutomaticPlan, AutomaticManager
from wanglibao_p2p.tasks import automatic_trade
from wanglibao_pay.models import Card, Bank, PayInfo
from wanglibao_sms.utils import validate_validation_code, send_validation_code
from wanglibao_account.models import VerifyCounter, Binding, Message, UserAddress
from rest_framework.permissions import IsAuthenticated
from wanglibao.const import ErrorNumber
from wanglibao.templatetags.formatters import safe_phone_str
from order.models import Order
from wanglibao_announcement.utility import AnnouncementAccounts
from django.template.defaulttags import register
from wanglibao_p2p.keeper import EquityKeeperDecorator
from order.utils import OrderHelper
from wanglibao_redpack import backends
from wanglibao_rest import utils
from wanglibao_activity.models import ActivityRecord


# from wanglibao.settings import CJDAOKEY
# from wanglibao_account.tasks import cjdao_callback
# from wanglibao.settings import RETURN_REGISTER

from wanglibao.settings import TINMANGKEY, RETURN_TINMANG_URL, \
    PROMO_TOKEN_QUERY_STRING, CALLBACK_HOST, YIRUITE_AD_KEY_TEST, \
    RETURN_YIRUITE_URL_TEST
from wanglibao_account.tasks import tianmang_callback, yiruite_callback

logger = logging.getLogger(__name__)


class RegisterView(RegistrationView):
    template_name = "register.jade"
    form_class = EmailOrPhoneRegisterForm

    def register(self, request, **cleaned_data):
        nickname = cleaned_data['nickname']
        password = cleaned_data['password']
        identifier = cleaned_data['identifier']
        invitecode = cleaned_data['invitecode']

        if User.objects.filter(wanglibaouserprofile__phone=identifier).first():
            return None

        user = create_user(identifier, password, nickname)
        if not user:
            return None

        set_promo_user(request, user, invitecode=invitecode)
        auth_user = authenticate(identifier=identifier, password=password)
        auth.login(request, auth_user)
        tools.register_ok.apply_async(kwargs={"user_id": auth_user.id, "device_type":"pc"})
        return user

    def get_success_url(self, request=None, user=None):
        if request.GET.get('next'):
            return request.GET.get('next')
        return '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super(RegisterView, self).get_context_data(**kwargs)
        context.update({
            'next': self.request.GET.get('next', '/accounts/login/')
        })
        return context


class EmailSentView(TemplateView):
    template_name = 'email_sent.jade'

    def get_context_data(self, **kwargs):
        return {
            'email': self.request.GET.get('email')
        }


@sensitive_post_parameters()
@csrf_protect
@login_required(login_url='/accounts/register/')
def password_change(request,
                    post_change_redirect=None,
                    password_change_form=PasswordChangeForm,
                    extra_context=None):
    if post_change_redirect is None:
        post_change_redirect = reverse('password_change_done')
    else:
        post_change_redirect = resolve_url(post_change_redirect)
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)

    # TODO find a proper status value and return error message
    return HttpResponse(status=400)


class PasswordResetValidateView(TemplateView):
    template_name = 'password_reset_phone.jade'

    def post(self):
        pass


class PasswordResetGetIdentifierView(TemplateView):
    template_name = 'password_reset.jade'

    def post(self, request, **kwargs):
        form = ResetPasswordGetIdentifierForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            identifier_type = detect_identifier_type(identifier)

            users = None
            if identifier_type == 'email':
                users = User.objects.filter(email=identifier, is_active=True)
            elif identifier_type == 'phone':
                users = User.objects.filter(wanglibaouserprofile__phone=identifier,
                                            wanglibaouserprofile__phone_verified=True)

            # There should be at most one user found
            assert len(users) <= 1

            if len(users) == 0:
                return HttpResponse(u"找不到该用户", status=400)
            else:
                view = PasswordResetValidateView()
                view.request = request
                # if identifier_type == 'phone':
                #     send_validation_code(identifier)
                request.session['user_to_reset'] = users[0].id
                return view.render_to_response({
                    'user_to_reset': users[0]
                })
        else:
            return HttpResponse(form.errors, status=400)

    def get_context_data(self, **kwargs):
        return {
            'form': ResetPasswordGetIdentifierForm()
        }


def send_validation_mail(request, **kwargs):
    user_id = request.session['user_to_reset']
    #user_email = get_user_model().objects.get(pk=user_id).email
    user_email = User.objects.get(pk=user_id).email

    form = PasswordResetForm(data={
        'email': user_email
    })

    if form.is_valid():
        form.save(request=request,
                  subject_template_name='registration/password_reset_subject.txt',
                  email_template_name='password_reset_email.html')
        return HttpResponse(u'验证邮件已发送，请您登录邮箱完成验证')
    else:
        return HttpResponse(u'没有有效的邮箱地址', status=500)


def send_validation_phone_code(request, **kwargs):
    user_id = request.session['user_to_reset']
    #user_phone = get_user_model().objects.get(pk=user_id).wanglibaouserprofile.phone
    user_phone = User.objects.get(pk=user_id).wanglibaouserprofile.phone
    phone_number = user_phone.strip()

    status, message = send_validation_code(phone_number)

    return HttpResponse(
        str({"message": message}), status=status)


def validate_phone_code(request):
    logger.info("Enter validate_phone_code")
    validate_code = request.POST['validate_code']
    user_id = request.session['user_to_reset']
    #user_phone = get_user_model().objects.get(pk=user_id).wanglibaouserprofile.phone
    user_phone = User.objects.get(pk=user_id).wanglibaouserprofile.phone
    phone_number = user_phone.strip()

    status, message = validate_validation_code(phone_number, validate_code)
    if status == 200:
        logger.debug("Phone code validated")
        request.session['phone_validated_time'] = (
            datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds()
        return HttpResponse('validate code succeeded', status=200)

    logger.debug("Phone code not valid")
    try:
        del request.session['phone_validated_time']
    except KeyError:
        pass
    return HttpResponse(message, status=status)


class ResetPassword(TemplateView):
    template_name = "password_reset_set_password.jade"

    def post(self, request):
        password1 = request.POST['password1'].strip()
        password2 = request.POST['password2'].strip()

        if password1 != password2:
            return HttpResponse(u'两次密码不匹配', status=400)

        if 'user_to_reset' not in request.session:
            return HttpResponse(u'没有用户信息', status=500)

        user_id = request.session['user_to_reset']
        #user = get_user_model().objects.get(pk=user_id)
        user = User.objects.get(pk=user_id)

        assert ('phone_validated_time' in request.session)
        last_validated_time = request.session['phone_validated_time']
        assert (last_validated_time != 0)

        if (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds() - last_validated_time < 30 * 60:
            user.set_password(password1)
            user.save()
            return HttpResponse(u'密码修改成功', status=200)

        else:
            return HttpResponse(u'验证超时，请重新验证', status=400)


class UserViewSet(PaginatedModelViewSet):
    #model = get_user_model()
    model = User
    serializer_class = UserSerializer
    permission_classes = IsAdminUser,


class AccountHome(TemplateView):
    template_name = 'account_home.jade'

    @register.filter(name="lookup")
    def get_item(dictionary, key):
        return dictionary.get(key)

    def get_context_data(self, **kwargs):
        message = ''
        user = self.request.user

        mode = 'p2p'
        fund_hold_info = []
        if self.request.path.rstrip('/').split('/')[-1] == 'fund':
            mode = 'fund'
            fund_hold_info = FundHoldInfo.objects.filter(user__exact=user)

        p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
            u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
        ]).select_related('product')

        # author: hetao; datetime: 2014.10.30; description: 加上活动所得收益
        earnings = Earning.objects.select_related('product__activity').filter(user=user)

        earning_map = {earning.product_id: earning for earning in earnings}
        result = []
        for equity in p2p_equities:
            obj = {"equity": equity}
            if earning_map.get(equity.product_id):
                obj["earning"] = earning_map.get(equity.product_id)
            #加息
            obj['hike'] = backends.get_hike(user, equity.product_id)

            result.append(obj)

        amortizations = ProductAmortization.objects.filter(product__in=[e.product for e in p2p_equities],
                                                           settled=False).prefetch_related("subs")

        unpayed_principle = 0
        for equity in p2p_equities:
            if equity.confirm:
                unpayed_principle += equity.unpaid_principal

        p2p_total_asset = user.margin.margin + user.margin.freeze + user.margin.withdrawing + unpayed_principle

        p2p_product_amortization = {}
        for amortization in amortizations:
            if not amortization.product_id in p2p_product_amortization:
                p2p_product_amortization[amortization.product_id] = amortization

        total_asset = p2p_total_asset

        #xunlei_vip = Binding.objects.filter(user=user).filter(btype='xunlei').first()

        #酒仙众筹用户
        tab_jiuxian = False
        jiuxian_selected = False
        equity_jiuxian = P2PEquityJiuxian.objects.filter(user=user).filter(product__category=u'酒仙众筹标').first()
        if equity_jiuxian:
            tab_jiuxian = True
            if equity_jiuxian.selected_at:
                jiuxian_selected = True
            # mode = 'jiuxian'

        if self.request.path.rstrip('/').split('/')[-1] == 'jiuxian':
            mode = 'jiuxian'

        return {
            'message': message,
            'result': result,
            'amortizations': amortizations,
            'p2p_product_amortization': p2p_product_amortization,
            'p2p_unpay_principle': unpayed_principle,
            'margin_withdrawing': user.margin.withdrawing,
            'margin_freeze': user.margin.freeze,
            'fund_hold_info': fund_hold_info,
            'p2p_total_asset': p2p_total_asset,
            'total_asset': total_asset,
            'mode': mode,
            'announcements': AnnouncementAccounts,
            'tab_jiuxian': tab_jiuxian,
            'equity_jiuxian': equity_jiuxian,
            'jiuxian_selected': jiuxian_selected
        }

    def post(self, request):
        select_type = request.POST.get('select_type')
        equity_jiuxian = P2PEquityJiuxian.objects.filter(user=self.request.user)\
            .filter(product__category=u'酒仙众筹标').first()
        if equity_jiuxian:
            equity_jiuxian.selected_type = select_type
            equity_jiuxian.selected_at = timezone.now()
            equity_jiuxian.save()
        return HttpResponseRedirect(reverse('accounts_address'))


class AccountHomeAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        user = request.user

        p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
            u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
        ]).select_related('product')

        unpayed_principle = 0
        p2p_total_paid_interest = 0
        p2p_total_unpaid_interest = 0
        p2p_total_interest = 0
        p2p_activity_interest = 0
        for equity in p2p_equities:
            if equity.confirm:
                unpayed_principle += equity.unpaid_principal  # 待收本金
                p2p_total_paid_interest += equity.pre_paid_interest  # 累积收益
                p2p_total_unpaid_interest += equity.unpaid_interest  # 待收益
                p2p_total_interest += equity.pre_total_interest  # 总收益
                p2p_activity_interest += equity.activity_interest  # 活动收益

        p2p_margin = user.margin.margin  # P2P余额
        p2p_freeze = user.margin.freeze  # P2P投资中冻结金额
        p2p_withdrawing = user.margin.withdrawing  # P2P提现中冻结金额
        p2p_unpayed_principle = unpayed_principle  # P2P待收本金

        p2p_total_asset = p2p_margin + p2p_freeze + p2p_withdrawing + p2p_unpayed_principle

        fund_hold_info = FundHoldInfo.objects.filter(user__exact=user)
        fund_total_asset = 0
        if fund_hold_info.exists():
            for hold_info in fund_hold_info:
                fund_total_asset += hold_info.current_remain_share + hold_info.unpaid_income

        today = timezone.datetime.today()
        total_income = DailyIncome.objects.filter(user=user).aggregate(Sum('income'))['income__sum'] or 0
        fund_income_week = DailyIncome.objects.filter(user=user, 
                            date__gt=today + datetime.timedelta(days=-8)).aggregate(Sum('income'))[ 'income__sum'] or 0
        fund_income_month = DailyIncome.objects.filter(user=user, 
                            date__gt=today + datetime.timedelta(days=-31)).aggregate(Sum('income'))['income__sum'] or 0

        res = {
            'total_asset': float(p2p_total_asset + fund_total_asset),  # 总资产
            'p2p_total_asset': float(p2p_total_asset),  # p2p总资产
            'p2p_margin': float(p2p_margin),  # P2P余额
            'p2p_freeze': float(p2p_freeze),  # P2P投资中冻结金额
            'p2p_withdrawing': float(p2p_withdrawing),  # P2P提现中冻结金额
            'p2p_unpayed_principle': float(p2p_unpayed_principle),  # P2P待收本金
            'p2p_total_unpaid_interest': float(p2p_total_unpaid_interest),  # p2p总待收益
            'p2p_total_paid_interest': float(p2p_total_paid_interest + p2p_activity_interest),  # P2P总累积收益
            'p2p_total_interest': float(p2p_total_interest),  # P2P总收益

            'fund_total_asset': float(fund_total_asset),  # 基金总资产
            'fund_total_income': float(total_income),  # 基金累积收益
            'fund_income_week': float(fund_income_week),  # 基金近一周收益(元)
            'fund_income_month': float(fund_income_month),  # 基金近一月收益(元)

        }

        return Response(res)


class AccountInviteView(TemplateView):
    template_name = 'invite.jade'

    def get_context_data(self, **kwargs):

        friends = IntroducedBy.objects.filter(introduced_by=self.request.user)
        friends_list = []
        friends_list.extend(friends)

        limit = 10
        paginator = Paginator(friends_list, limit)
        page = self.request.GET.get('page')

        try:
            friends_list = paginator.page(page)
        except PageNotAnInteger:
            friends_list = paginator.page(1)
        except Exception:
            friends_list = paginator.page(paginator.num_pages)

        dic = account_backends.broker_invite_list(self.request.user)
        return {
            'friends': friends_list,
            "earning": dic['first_earning'] + dic['second_earning'],
            "amount": dic['first_amount'] + dic['second_amount'],
            "first_amount": dic['first_amount'],
            "first_count": dic['first_count'],
            "second_amount": dic['second_amount'],
            "second_count": dic['second_count']
        }


class AccountInviteAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, **kwargs):
        introduces = IntroducedBy.objects.filter(introduced_by=request.user)
        res = []
        if not introduces:
            return Response({"ret_code":0, "data":res})

        for x in introduces:
            invite = {"name":x.user.wanglibaouserprofile.name,
                    "phone":safe_phone_str(x.user.wanglibaouserprofile.phone),
                    "created_at":timezone.get_current_timezone().normalize(x.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                    "is_id_valid":x.user.wanglibaouserprofile.id_is_valid}
            info = PayInfo.objects.filter(user=x.user, type="D", status=u"成功").first()
            if not info:
                invite['pay'] = False
            else:
                invite['pay'] = True
            rd = P2PRecord.objects.filter(user=x.user, catalog=u"申购").first()
            if not rd:
                invite['buy'] = False
            else:
                invite['buy'] = True
            res.append(invite)
        return Response({"ret_code":0, "data":res})

class AccountInviteAllGoldAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, **kwargs):
        dic = account_backends.broker_invite_list(request.user)
        users = dic['users']
        first_amount, first_earning, second_amount, second_earning = dic['first_amount'],\
                dic['first_earning'], dic['second_amount'], dic['second_earning']
        first_count, second_count = dic['first_count'], dic['second_count']
        first_intro = dic['first_intro']
        commission = dic['commission']
        

        introduces = IntroducedBy.objects.filter(introduced_by=request.user).select_related("user__wanglibaouserprofile").all()
        keys = commission.keys()
        for x in introduces:
            user_id = x.user.id
            if user_id in keys:
                first_intro.append([safe_phone_str(users[user_id].phone), 
                                commission[user_id]['amount'], commission[user_id]['earning']])
            else:
                first_intro.append([safe_phone_str(x.user.wanglibaouserprofile.phone), 0, 0])

        return Response({"ret_code":0, "first":{"amount":first_amount, 
                        "earning":first_earning, "count":first_count, "intro":first_intro},
                        "second":{"amount":second_amount, "earning":second_earning,
                        "count":second_count}, "count":len(introduces)})

class AccountInviteIncomeAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, **kwargs):
        earning = account_backends.invite_earning(request.user)
        return Response({"ret_code":0, "earning":earning})

class AccountInviteHikeAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, **kwargs):
        nums = IntroducedBy.objects.filter(introduced_by=request.user).count()

        hikes = backends.get_hike_nums(request.user)
        amount = backends.get_hike_amount(request.user)
        thity = ActivityRecord.objects.filter(user=request.user, gift_type='phonefare', msg_type='message').aggregate(Sum('income'))
        if thity['income__sum']:
            callfee = thity['income__sum']
        else:
            callfee = 0
        prot = P2PRecord.objects.filter(user=request.user, catalog=u'申购').order_by('-create_time').first()
        if not prot:
            product_id = 0
        else:
            product_id = prot.product_id

        return Response({"ret_code":0, "intro_nums":nums, "hikes":hikes,
                        "call_charge":30, "total_hike":"0.1%", "calls":callfee,
                        "amount":amount, "product_id":product_id})

class AccountP2PRecordAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        user = request.user
        # p2p_equities = P2PEquity.objects.filter(user=user).all().select_related('product')
        p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
            u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
        ]).select_related('product')

        page = request.GET.get('page', 0)
        try:
            page = int(page)
            if page < 0:
                return Response({"detail": "Query String must be a number."}, status=404)
        except:
            return Response({"detail": "Query String must be a number."}, status=404)

        if page != 0:

            limit = 2
            paginator = Paginator(p2p_equities, limit)

            try:
                p2p_equities = paginator.page(page)
            except PageNotAnInteger:
                p2p_equities = paginator.page(1)
            except Exception:
                p2p_equities = paginator.page(paginator.num_pages)

        p2p_records = [{
                           'equity_created_at': timezone.localtime(equity.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                           # 投标时间
                           'equity_product_short_name': equity.product.short_name,  # 产品名称
                           'equity_product_expected_earning_rate': equity.product.expected_earning_rate,  # 年化收益(%)
                           'equity_product_period': equity.product.period,  # 产品期限(月)*
                           'equity_equity': float(equity.equity),  # 用户所持份额(投资金额)
                           'equity_product_display_status': equity.product.display_status,  # 状态
                           'equity_term': equity.term,  # 还款期
                           'equity_product_amortization_count': equity.product.amortization_count,  # 还款期数
                           'equity_paid_interest': float(equity.pre_paid_interest),  # 单个已经收益
                           'equity_total_interest': float(equity.pre_total_interest),  # 单个预期收益
                           'equity_contract': 'https://%s/api/p2p/contract/%s/' % (
                               request.get_host(), equity.product.id),  # 合同
                           'product_id': equity.product_id
                       } for equity in p2p_equities]

        if int(page) != 0:
            res = {
                'total_counts': p2p_equities.paginator.count,  # 总条目数
                'total_page': int(math.ceil(p2p_equities.paginator.count / float(p2p_equities.paginator.per_page))),
                # 总页数
                'per_page_number': p2p_equities.paginator.per_page,  # 每页显示条数
                'pre_page': p2p_equities.previous_page_number() if p2p_equities.has_previous() else None,  # 前一页页码
                'next_page': p2p_equities.next_page_number() if p2p_equities.has_next() else None,  # 后一页页码
                'p2p_records': p2p_records,
            }
        else:
            res = p2p_records
        return Response(res)


class AccountFundRecordAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        user = request.user
        fund_hold_info = FundHoldInfo.objects.filter(user__exact=user)

        limit = 20
        paginator = Paginator(fund_hold_info, limit)
        page = request.GET.get('page')

        try:
            fund_hold_info = paginator.page(page)
        except PageNotAnInteger:
            fund_hold_info = paginator.page(1)
        except Exception:
            fund_hold_info = paginator.page(paginator.num_pages)

        fund_records = [{
                            'fund_fund_name': fund.fund_name,  # 基金产品名称
                            'fund_current_remain_share': float(fund.current_remain_share),  # 当前份额余额
                            'fund_unpaid_income': float(fund.unpaid_income),  # 未付收益
                            'fund_code': fund.fund_code,  # 基金代码
                        } for fund in fund_hold_info]

        res = {
            'total_counts': fund_hold_info.paginator.count,
            'total_page': round(fund_hold_info.paginator.count / fund_hold_info.paginator.per_page),
            'per_page_number': fund_hold_info.paginator.per_page,
            'pre_page': fund_hold_info.previous_page_number() if fund_hold_info.has_previous() else None,
            'next_page': fund_hold_info.next_page_number() if fund_hold_info.has_next() else None,
            'fund_records': fund_records,
        }
        return Response(res)


class AccountP2PAssetAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        user = request.user

        p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
            u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
        ]).select_related('product')

        unpayed_principle = 0
        p2p_total_paid_interest = 0
        p2p_total_interest = 0
        p2p_total_unpaid_interest = 0
        for equity in p2p_equities:
            if equity.confirm:
                unpayed_principle += equity.unpaid_principal
                p2p_total_unpaid_interest += equity.unpaid_interest
                p2p_total_paid_interest += equity.paid_interest
                p2p_total_interest += equity.total_interest

        p2p_margin = user.margin.margin
        p2p_freeze = user.margin.freeze
        p2p_withdrawing = user.margin.withdrawing
        p2p_unpayed_principle = unpayed_principle

        p2p_total_asset = p2p_margin + p2p_freeze + p2p_withdrawing + p2p_unpayed_principle

        res = {

            'p2p_total_asset': float(p2p_total_asset),  # 总资产
            'p2p_margin': float(p2p_margin),  # P2P余额
            'p2p_freeze': float(p2p_freeze),  # P2P投资中冻结金额
            'p2p_withdrawing': float(p2p_withdrawing),  # P2P提现中冻结金额
            'p2p_unpayed_principle': float(p2p_unpayed_principle),  # P2P待收本金
            'p2p_total_unpaid_interest': float(p2p_total_unpaid_interest),  # p2p总待收益
            'p2p_total_paid_interest': float(p2p_total_paid_interest),  # P2P总累积收益
            'p2p_total_interest': float(p2p_total_interest),  # P2P总收益

        }
        return Response(res)


class AccountFundAssetAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        user = request.user
        fund_hold_info = FundHoldInfo.objects.filter(user__exact=user)
        fund_total_asset = 0
        if fund_hold_info.exists():
            for hold_info in fund_hold_info:
                fund_total_asset += hold_info.current_remain_share + hold_info.unpaid_income

        today = timezone.datetime.today()

        total_income = DailyIncome.objects.filter(user=user).aggregate(Sum('income'))['income__sum'] or 0
        fund_income_week = \
            DailyIncome.objects.filter(user=user, date__gt=today + datetime.timedelta(days=-8)).aggregate(
                Sum('income'))[
                'income__sum'] or 0
        fund_income_month = \
            DailyIncome.objects.filter(user=user, date__gt=today + datetime.timedelta(days=-31)).aggregate(
                Sum('income'))[
                'income__sum'] or 0

        res = {
            'fund_total_asset': float(fund_total_asset),  # 基金总资产
            'fund_total_income': float(total_income),  # 基金累积收益
            'fund_income_week': float(fund_income_week),  # 基金近一周收益(元)
            'fund_income_month': float(fund_income_month),  # 基金近一月收益(元)
        }
        return Response(res)


class FundInfoAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        user = self.request.user

        try:
            fetcher = UserInfoFetcher(user)
            fetcher.fetch_user_fund_hold_info()
        except FetchException:
            message = u'获取数据失败，请稍后重试'
        except AccessException:
            pass

        fund_hold_info = FundHoldInfo.objects.filter(user__exact=user)

        fund_total_asset = 0
        income_rate = 0

        if fund_hold_info.exists():
            for hold_info in fund_hold_info:
                fund_total_asset += hold_info.current_remain_share + hold_info.unpaid_income

        today = timezone.datetime.today()

        total_income = DailyIncome.objects.filter(user=user).aggregate(Sum('income'))['income__sum'] or 0
        fund_income_week = \
            DailyIncome.objects.filter(user=user, date__gt=today + datetime.timedelta(days=-8)).aggregate(
                Sum('income'))[
                'income__sum'] or 0
        fund_income_month = \
            DailyIncome.objects.filter(user=user, date__gt=today + datetime.timedelta(days=-31)).aggregate(
                Sum('income'))[
                'income__sum'] or 0

        if fund_total_asset != 0:
            income_rate = total_income / fund_total_asset

        return Response({
                            'income_rate': income_rate,
                            'fund_income_week': fund_income_week,
                            'fund_income_month': fund_income_month,
                            'fund_total_asset': fund_total_asset,
                            'total_income': total_income,
                        }, status=200)


class AccountTransaction(TemplateView):
    template_name = 'account_transaction.jade'

    def get_context_data(self, **kwargs):
        message = ''
        try:
            fetcher = UserInfoFetcher(self.request.user)
            fetcher.fetch_user_trade_history()
        except FetchException:
            message = u'获取数据失败，请稍后重试'
        except AccessException:
            pass

        transactions = TradeHistory.objects.filter(user__exact=self.request.user)
        pager = Paginator(transactions, 20)
        page = self.request.GET.get('page')
        if not page:
            page = 1
        transactions = pager.page(page)
        return {
            "transactions": transactions,
            "message": message,
            'announcements': AnnouncementAccounts
        }


class AccountTransactionP2P(TemplateView):
    template_name = 'account_transaction_p2p.jade'

    def get_context_data(self, **kwargs):
        trade_records = P2PRecord.objects.filter(user=self.request.user)
        pager = Paginator(trade_records, 20)
        page = self.request.GET.get('page')
        if not page:
            page = 1
        trade_records = pager.page(page)
        for t in trade_records:
            status = Order.objects.filter(id=t.order_id).first().status
            if status == "":
                t.status = "异常"
            else:
                t.status = status
        return {
            "trade_records": trade_records,
            'announcements': AnnouncementAccounts
        }

class AccountRedPacket(TemplateView):
    template_name = 'redpacket_available.jade'

    def get_context_data(self, **kwargs):

        status = kwargs['status']
        if status not in ('used', 'unused', 'expires'):
            status = 'unused'

        user = self.request.user
        device = utils.split_ua(self.request)
        result = backends.list_redpack(user, 'all', device['device_type'])
        red_packets = result['packages'].get(status, [])

        return {
            "red_packets": red_packets,
            "status": status
        }


class AccountTransactionDeposit(TemplateView):
    template_name = 'account_transaction_deposit.jade'

    def get_context_data(self, **kwargs):
        pay_records = PayInfo.objects.filter(user=self.request.user, type=PayInfo.DEPOSIT).exclude(
            status=PayInfo.PROCESSING)
        pager = Paginator(pay_records, 20)
        page = self.request.GET.get('page')
        if not page:
            page = 1
        pay_records = pager.page(page)
        return {
            "pay_records": pay_records,
            'announcements': AnnouncementAccounts
        }


class AccountTransactionWithdraw(TemplateView):
    template_name = 'account_transaction_withdraw.jade'

    def get_context_data(self, **kwargs):
        pay_records = PayInfo.objects.filter(user=self.request.user, type=PayInfo.WITHDRAW)
        pager = Paginator(pay_records, 20)
        page = self.request.GET.get('page')
        if not page:
            page = 1
        pay_records = pager.page(page)
        return {
            "pay_records": pay_records,
            'announcements': AnnouncementAccounts
        }


class AccountRepayment(TemplateView):
    template_name = 'account_repayment.jade'

    def get_context_data(self, **kwargs):
        repayment_records = AmortizationRecord.objects.select_related('amortization_product').filter(
            user=self.request.user)
        pager = Paginator(repayment_records, 20)
        page = self.request.GET.get('page')
        if not page:
            page = 1
        repayment_records = pager.page(page)
        return {
            "repayment_records": repayment_records,
            'announcements': AnnouncementAccounts
        }


class AccountBankCard(TemplateView):
    template_name = 'account_bankcard.jade'

    def get_context_data(self, **kwargs):
        message = ''
        try:
            fetcher = UserInfoFetcher(self.request.user)
            fetcher.fetch_bind_banks()
        except FetchException:
            message = u'获取数据失败，请稍后重试'
        except AccessException:
            pass

        cards = BindBank.objects.filter(user__exact=self.request.user)
        p2p_cards = Card.objects.filter(user__exact=self.request.user)
        banks = Bank.get_withdraw_banks()
        return {
            "cards": cards,
            'p2p_cards': p2p_cards,
            'banks': banks,
            'user_profile': self.request.user.wanglibaouserprofile,
            "message": message,
            'announcements': AnnouncementAccounts
        }


class ResetPasswordAPI(APIView):
    permission_classes = ()

    def post(self, request):
        password = request.DATA.get('new_password', "")
        identifier = request.DATA.get('identifier', "")
        validate_code = request.DATA.get('validate_code', "")

        identifier = identifier.strip()
        password = password.strip()
        validate_code = validate_code.strip()

        if not password or not identifier or not validate_code:
            return Response({'ret_code': 30002, 'message': u'信息输入不完整'})

        if not 6 <= len(password) <= 20:
            return Response({'ret_code': 30001, 'message': u'密码需要在6-20位之间'})

        identifier_type = detect_identifier_type(identifier)

        if identifier_type == 'phone':
            #user = get_user_model().objects.get(wanglibaouserprofile__phone=identifier)
            user = User.objects.get(wanglibaouserprofile__phone=identifier)
        else:
            return Response({'ret_code': 30003, 'message': u'请输入手机号码'})

        status, message = validate_validation_code(identifier, validate_code)
        if status == 200:
            user.set_password(password)
            user.save()
            return Response({'ret_code': 0, 'message': u'修改成功'})
        else:
            return Response({'ret_code': 30004, 'message': u'验证码验证失败'})


class Third_login(View):
    def get(self, request, login_type):
        url = third_login.assem_params(login_type, request)
        return HttpResponseRedirect(url)


class Third_login_back(APIView):
    permission_classes = ()

    def get(self, request):
        result = third_login.login_back(request)
        return Response(result)


class ChangePasswordAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        new_password = request.DATA.get('new_password', "").strip()
        old_password = request.DATA.get('old_password', "").strip()
        validate_code = request.DATA.get('validate_code', "").strip()

        if not old_password or not new_password or not validate_code:
            return Response({'ret_code': 30041, 'message': u'信息输入不完整'})

        if not 6 <= len(new_password) <= 20:
            return Response({'ret_code': 30042, 'message': u'密码需要在6-20位之间'})

        user = request.user
        if not user.check_password(old_password):
            return Response({'ret_code': 30043, 'message': u'原密码错误'})

        status, message = validate_validation_code(user.wanglibaouserprofile.phone, validate_code)
        if status != 200:
            return Response({"ret_code": 30044, "message": u"验证码输入错误"})

        user.set_password(new_password)
        user.save()
        return Response({'ret_code': 0, 'message': u'修改成功'})


class MessageView(TemplateView):
    template_name = 'message.jade'

    def get_context_data(self, **kwargs):
        listtype = self.request.GET.get("listtype")

        if not listtype or listtype not in ("read", "unread", "all"):
            listtype = 'all'

        if listtype == "unread":
            messages = Message.objects.filter(target_user=self.request.user, read_status=False, notice=True).order_by(
                '-message_text__created_at')
        elif listtype == "read":
            messages = Message.objects.filter(target_user=self.request.user, read_status=True, notice=True).order_by(
                '-message_text__created_at')
        else:
            messages = Message.objects.filter(target_user=self.request.user).order_by('-message_text__created_at')

        messages_list = []
        messages_list.extend(messages)

        limit = 10
        paginator = Paginator(messages_list, limit)
        page = self.request.GET.get('page')

        try:
            messages_list = paginator.page(page)
        except PageNotAnInteger:
            messages_list = paginator.page(1)
        except Exception:
            messages_list = paginator.page(paginator.num_pages)

        return {
            'messageList': messages_list,
            'list_type': listtype
        }


class MessageListAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        result = inside_message.list_msg(request.DATA, request.user)
        return Response(result)


class MessageCountAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        result = inside_message.count_msg(request.DATA, request.user)
        return Response(result)


class MessageDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, message_id):
        result = inside_message.sign_read(request.user, message_id)
        return Response(result)


@sensitive_post_parameters()
@csrf_protect
@never_cache
def ajax_login(request, authentication_form=EmailOrPhoneAuthenticationForm):
    def messenger(message, user=None):
        res = dict()
        if user:
            res['nick_name'] = user.wanglibaouserprofile.nick_name
        res['message'] = message
        return json.dumps(res)

    if request.method == "POST":

        if request.is_ajax():
            form = authentication_form(request, data=request.POST)
            if form.is_valid():
                auth_login(request, form.get_user())

                if request.POST.has_key('remember_me'):
                    request.session.set_expiry(604800)
                else:
                    request.session.set_expiry(1800)
                return HttpResponse(messenger('done', user=request.user))
            else:
                return HttpResponseForbidden(messenger(form.errors))
        else:
            return HttpResponseForbidden('not valid ajax request')
    else:
        return HttpResponseNotAllowed(["GET"])


@sensitive_post_parameters()
@csrf_protect
@never_cache
def ajax_register(request):
    def messenger(message, user=None):
        res = dict()
        if user:
            res['nick_name'] = user.wanglibaouserprofile.nick_name
        res['message'] = message
        return json.dumps(res)

    if request.method == "POST":
        if request.is_ajax():
            form = EmailOrPhoneRegisterForm(request.POST)
            if form.is_valid():
                nickname = form.cleaned_data['nickname']
                password = form.cleaned_data['password']
                identifier = form.cleaned_data['identifier']
                invitecode = form.cleaned_data['invitecode']

                if User.objects.filter(wanglibaouserprofile__phone=identifier).first():
                    return HttpResponse(messenger('error'))

                user = create_user(identifier, password, nickname)
                if not user:
                    return HttpResponse(messenger('error'))

                cooperation_process(request, user)

                auth_user = authenticate(identifier=identifier, password=password)

                auth.login(request, auth_user)

                tools.register_ok.apply_async(kwargs={"user_id": auth_user.id, "device_type":"pc"})

                return HttpResponse(messenger('done', user=request.user))
            else:
                return HttpResponseForbidden(messenger(form.errors))
        else:
            return HttpResponseForbidden('not valid ajax request')
    else:
        return HttpResponseNotAllowed(["GET"])

def cooperation_process(request, user, invitecode):
    """
    处理第三方渠道
    """
    if (request.session.get(PROMO_TOKEN_QUERY_STRING) == 'yiruite') and request.session.get('yiruite_tid'):
        set_promo_user(request, user, invitecode=request.session.get(PROMO_TOKEN_QUERY_STRING))
        yiruite_process(request, user)
    elif (request.session.get('tianmang_source') == 'tianmang') and request.session.get('tianmang_sn'):
        set_promo_user(request, user, invitecode=request.session.get('tianmang_source'))
        tianmang_process(request, user)
    else:
        set_promo_user(request, user, invitecode=invitecode)


def yiruite_process(request, user):
    """
    易瑞特回调处理，需要保存yiruite_tid到Binding表中
    """
    yiruite_tid = request.session.get('yiruite_tid', None)
    if yiruite_tid:
        binding = Binding()
        binding.user = user
        binding.btype = 'yiruite'
        binding.bid = yiruite_tid
        binding.save()

        sign = yiruite_tid + user.wanglibaouserprofile.phone + YIRUITE_AD_KEY_TEST
        params = {
            "tid": yiruite_tid,
            "uid": hashlib.md5(user.wanglibaouserprofile.phone).hexdigest(),
            "ad_key": YIRUITE_AD_KEY_TEST,
            "sign": hashlib.md5(sign).hexdigest(),
            "ip": CALLBACK_HOST
        }
        yiruite_callback.apply_async(kwargs={'url': RETURN_YIRUITE_URL_TEST, 'params': params})

        # request.session['yiruite_from'] = None
        request.session['yiruite_tid'] = None
    return True

def tianmang_process(request, user):
    """
    根据url判断是否是从天芒注册的, 如果是返回invitecode为tianmang
    :param request:
    :param user:
    :param invitecode:
    :return: 如果是天芒注册的返回invitecode为"tianmang" 否则是原始的invitecode
    """
    sn = request.session.get('tianmang_sn', None)
    if sn:
        #注册成功后向天芒云 发送注册成功请求

        params={
            "oid": TINMANGKEY,
            "sn" : sn,
            "uid": hashlib.md5(user.wanglibaouserprofile.phone).hexdigest(),
            "uname": user.wanglibaouserprofile.name,
            "method": "json"
        }
        tianmang_callback.apply_async(kwargs={'url': RETURN_TINMANG_URL, 'params': params})

        request.session['tianmang_source'] = None
        request.session['tianmang_sn'] = None
    return True

class P2PAmortizationView(TemplateView):
    template_name = 'p2p_amortization_plan.jade'

    def get_context_data(self, **kwargs):
        product_id = kwargs['product_id']

        equity = P2PEquity.objects.filter(user=self.request.user, product_id=product_id).prefetch_related(
            'product').first()

        amortizations = UserAmortization.objects.filter(user=self.request.user,
                                                        product_amortization__product_id=product_id)
        return {
            'equity': equity,
            'amortizations': amortizations,
            'announcements': AnnouncementAccounts
        }


class P2PAmortizationAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, **kwargs):
        user = request.user
        product_id = kwargs['product_id']

        equity = P2PEquity.objects.filter(user=user, product_id=product_id).prefetch_related('product').first()
        if not equity:
            return Response({'ret_code': -1, 'message': u'该产品用户持仓信息为空'})

        amortizations = UserAmortization.objects.filter(user=self.request.user,
                                                        product_amortization__product_id=product_id)

        amortization_record = [{
                                   'amortization_term_date': timezone.localtime(amortization.term_date).strftime(
                                       "%Y-%m-%d %H:%M:%S"),  # 还款时间
                                   'amortization_principal': float(amortization.principal),  # 本金
                                   'amortization_amount_interest': float(amortization.interest),  # 利息
                                   'amortization_amount': float(amortization.principal + amortization.interest),  # 总记
                               } for amortization in amortizations]

        res = {
            'equity_product_short_name': equity.product.short_name,  # 还款标题
            'equity_product_serial_number': equity.product.serial_number,  # 还款计划编号
            'amortization_record': amortization_record

        }
        return Response(res)


@login_required
def user_product_contract(request, product_id):
    equity = P2PEquity.objects.filter(user=request.user, product_id=product_id).prefetch_related('product').first()

    product = equity.product
    order = OrderHelper.place_order(order_type=u'生成合同文件', status=u'开始', equity_id=equity.id, product_id=product.id)

    if not equity.latest_contract:
        #create contract file
        EquityKeeperDecorator(product, order.id).generate_contract_one(equity_id=equity.id, savepoint=False)

    equity_new = P2PEquity.objects.filter(id=equity.id).first()
    try:
        f = equity_new.latest_contract
        lines = f.readlines()
        f.close()
        return HttpResponse("\n".join(lines))
    except ValueError, e:
        raise Http404


class UserProductContract(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, product_id):
        equity = P2PEquity.objects.filter(user=request.user, product_id=product_id).prefetch_related('product').first()
        if not equity:
            return Response({
                'message': u'合同没有找到',
                'error_number': ErrorNumber.contract_not_found
            })
        product = equity.product
        order = OrderHelper.place_order(order_type=u'生成合同文件', status=u'开始', equity_id=equity.id, product_id=product.id)

        if not equity.latest_contract:
            #create contract file
            EquityKeeperDecorator(product, order.id).generate_contract_one(equity_id=equity.id, savepoint=False)

        equity_new = P2PEquity.objects.filter(id=equity.id).first()

        try:
            f = equity_new.latest_contract
            lines = f.readlines()
            f.close()
            return HttpResponse("\n".join(lines))
        except:
            return Response({
                'message': u'合同没有找到',
                'error_number': ErrorNumber.contract_not_found
            })


@login_required
def test_contract(request, equity_id):
    p2p_equity = P2PEquity.objects.filter(id=equity_id).select_related('product').first()
    p2p_equities = P2PEquity.objects.select_related('user__wanglibaouserprofile', 'product__contract_template').filter(product=p2p_equity.product)
    contract_info = P2PProductContract.objects.filter(product=p2p_equity.product).first()
    p2p_equity.contract_info = contract_info
    return HttpResponse(generate_contract(p2p_equity, 'tongchenghuodi_template.jade', p2p_equities))


class IdVerificationView(TemplateView):
    template_name = 'verify_id.jade'
    form_class = IdVerificationForm
    success_url = '/accounts/id_verify/'

    def get_context_data(self, **kwargs):
        counter = VerifyCounter.objects.filter(user=self.request.user).first()
        count = 0
        if counter:
            count = counter.count
        return {
            'user': self.request.user,
            'counter': count
        }

    def form_valid(self, form):
        user = self.request.user

        user.wanglibaouserprofile.id_number = form.cleaned_data.get('id_number')
        user.wanglibaouserprofile.name = form.cleaned_data.get('name')
        user.wanglibaouserprofile.id_is_valid = True
        user.wanglibaouserprofile.id_valid_time = timezone.now()
        user.wanglibaouserprofile.save()

        return super(IdVerificationView, self).form_valid(form)


class AdminIdVerificationView(TemplateView):
    template_name = 'admin_verify_id.jade'


class AdminSendMessageView(TemplateView):
    template_name = "admin_send_message.jade"


class AdminSendMessageAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        phone = request.DATA.get("phone", "")
        title = request.DATA.get("title", "")
        content = request.DATA.get("content", "")
        mtype = request.DATA.get("mtype", "")
        if not phone or not title or not content or not mtype:
            return Response({"ret_code": 1, "message": "信息输入不完整"})
        user = User.objects.filter(wanglibaouserprofile__phone=phone).first()
        if not user:
            return Response({"ret_code": 1, "message": "没有此用户"})

        inside_message.send_one.apply_async(kwargs={
            "user_id": user.id,
            "title": title,
            "content": content,
            "mtype": mtype
        })
        return Response({"ret_code": 0, "message": "发送成功"})


class IntroduceRelation(TemplateView):
    template_name = 'introduce_add.jade'

    def post(self, request):
        user_phone = request.POST.get('user_phone', '').strip()
        introduced_by_phone = request.POST.get('introduced_by_phone', '').strip()
        bought_at = request.POST.get('bought_at', '').strip()
        gift_send_at = request.POST.get('gift_send_at', '').strip()
        try:
            user = User.objects.get(wanglibaouserprofile__phone=user_phone)
        except User.DoesNotExist:
            return HttpResponse({
                u"没有找到 %s 该记录" % user_phone
            })
        try:
            introduced_by = User.objects.get(wanglibaouserprofile__phone=introduced_by_phone)
        except User.DoesNotExist:
            return HttpResponse({
                u"没有找到 %s 该记录" % user_phone
            })
        try:
            introduce = IntroducedBy.objects.get(user=user, introduced_by=introduced_by)
        except IntroducedBy.DoesNotExist:
            record = IntroducedBy()
            record.introduced_by = introduced_by
            record.user = user
            if bought_at:
                print(bought_at)
                record.bought_at = bought_at
            if gift_send_at:
                print(gift_send_at)
                record.gift_send_at = gift_send_at
            record.created_by = request.user
            record.save()
            return HttpResponse({
                u" %s与%s的邀请关系已经确定" % (user_phone, introduced_by)
            })

        return HttpResponse({
            u" %s与%s的邀请关系已经存在" % (user_phone, introduced_by)
        })

    @method_decorator(permission_required('marketing.add_introducedby'))
    def dispatch(self, request, *args, **kwargs):
        """
        Only user with change payinfo permission can call this view
        """
        return super(IntroduceRelation, self).dispatch(request, *args, **kwargs)


class AddressView(TemplateView):
    template_name = 'account_address.jade'

    def get_context_data(self, **kwargs):

        address_list = UserAddress.objects.filter(user=self.request.user).order_by('-id')

        return {
            'address_list': address_list
        }


class AddressListAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        address_list = UserAddress.objects.filter(user=request.user).order_by('-id')
        if address_list:
            address_list = [{
                'id': address.id,
                'name': address.name,
                'phone_number': address.phone_number,
                'address': address.address,
                'postcode': address.postcode,
                'is_default': address.is_default,
                'province': address.province,
                'city': address.city,
                'area': address.area
            } for address in address_list]
            return Response({
                'ret_code': 0,
                'message': 'ok',
                'address': address_list
            })
        else:
            return Response({'ret_code': 3000, 'message': u'没有收货地址'})


class AddressAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        address_id = request.DATA.get('address_id', "").strip()
        address_name = request.DATA.get('name', "").strip()
        phone_number = request.DATA.get('phone_number', "").strip()
        address_address = request.DATA.get('address', "").strip()
        postcode = request.DATA.get('postcode', "").strip()
        province = request.DATA.get('province', "").strip()
        city = request.DATA.get('city', "").strip()
        area = request.DATA.get('area', "").strip()
        is_default = request.DATA.get('is_default', False)
        is_default = True if is_default == 'true' else False

        if not address_name or not phone_number or not address_address:
            return Response({'ret_code': 3001, 'message': u'信息输入不完整'})
        if len(phone_number) > 15:
            return Response({'ret_code': 3004, 'message': u'联系电话不能超过15位'})

        if is_default:
            """ clear the exists is_default value """
            UserAddress.objects.filter(user=request.user).update(is_default=False)

        if address_id:
            try:
                address = UserAddress.objects.get(id=address_id)
                address.user = request.user
                address.name = address_name
                address.address = address_address
                address.province = province
                address.city = city
                address.area = area
                address.phone_number = phone_number
                address.postcode = postcode
                address.is_default = is_default
                address.save()
                return Response({'ret_code': 0, 'message': u'修改成功'})
            except:
                return Response({'ret_code': 3003, 'message': u'地址不存在'})
        else:
            address = UserAddress()
            address.user = request.user
            address.name = address_name
            address.address = address_address
            address.province = province
            address.city = city
            address.area = area
            address.phone_number = phone_number
            address.postcode = postcode
            address.is_default = is_default
            address.save()
            return Response({'ret_code': 0, 'message': u'添加成功'})


class AddressDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        address_id = request.DATA.get('address_id', "").strip()

        if not address_id:
            return Response({'ret_code': 3002, 'message': u'ID错误'})

        try:
            address = UserAddress.objects.get(id=address_id)
            address.delete()
            return Response({
                'ret_code': 0,
                'message': u'删除成功'
            })
        except:
            return Response({'ret_code': 3003, 'message': u'地址不存在'})


class AddressGetAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, address_id):
        if not address_id:
            return Response({'ret_code': 3002, 'message': u'ID错误'})

        try:
            address = UserAddress.objects.get(id=address_id)
            if address:
                address = {
                    'address_id': address.id,
                    'name': address.name,
                    'phone_number': address.phone_number,
                    'address': address.address,
                    'postcode': address.postcode,
                    'is_default': address.is_default,
                    'province': address.province,
                    'city': address.city,
                    'area': address.area
                }
                return Response({
                    'ret_code': 0,
                    'message': 'ok',
                    'address': address
                })
            else:
                return Response({'ret_code': 3000, 'message': u'没有收货地址'})
        except:
            return Response({'ret_code': 3003, 'message': u'地址不存在'})


class AutomaticView(TemplateView):
    template_name = 'account_auto_tender.jade'

    def get_context_data(self, **kwargs):
        status, message, result = False, '', {}
        automatic_manager = AutomaticManager.objects.filter(Q(is_used=True), Q(stop_plan=AutomaticManager.STOP_PLAN_STOP) | Q(stop_plan=AutomaticManager.STOP_PLAN_PAUSE) & Q(start_at__lte=timezone.now()) & Q(end_at__gte=timezone.now()))
        if automatic_manager.exists():
            status, message = True, automatic_manager.first().message

        plan = AutomaticPlan.objects.filter(user=self.request.user).first()
        if plan is not None:
            result = {
                'id': plan.id,
                'amounts_auto': int(plan.amounts_auto),
                'period_min': plan.period_min,
                'period_max': plan.period_max,
                'rate_min': int(plan.rate_min),
                'rate_max': int(plan.rate_max),
                'is_used': plan.is_used
            }

        return {
            'margin': self.request.user.margin.margin,
            'plan': result,
            'status': status,
            'message': message

        }


class AutomaticApiView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        # 开启功能，需要同时校验数据
        # 关闭操作，用户自动投标设置数据，只更改状态
        is_used = request.DATA.get('is_used', False)

        if not is_used:
            # close plan
            plan = AutomaticPlan.objects.filter(user=request.user).first()
            if plan:
                plan.is_used = False
                plan.save()

            return Response({
                'ret_code': 0,
                'message': u'自动投标计划关闭成功'
            })

        amounts_auto = request.DATA.get('amounts_auto', Decimal(0))
        period_min = request.DATA.get('period_min', 0)
        period_max = request.DATA.get('period_max', 0)
        rate_min = request.DATA.get('rate_min', 0)
        rate_max = request.DATA.get('rate_max', 0)

        if not amounts_auto or not period_min or not period_max or not rate_min or not rate_max:
            return Response({'ret_code': 3001, 'message': u'信息输入不完整'})

        try:
            if Decimal(amounts_auto) < 100:
                return Response({'ret_code': 3002, 'message': u'自动投标金额必须大于等于100'})
            if Decimal(amounts_auto) % 100 != 0:
                return Response({'ret_code': 3003, 'message': u'自动投标金额必须是100的整数倍'})
            if Decimal(amounts_auto) > self.request.user.margin.margin:
                return Response({'ret_code': 3003, 'message': u'自动投标金额不能够大于账户可用余额'})
        except:
            return Response({'ret_code': 3004, 'message': u'自动投标金额输入不合法'})

        try:
            if int(period_min) > int(period_max):
                return Response({'ret_code': 3005, 'message': u'产品投资最大期限不允许小于最小期限'})
        except:
            return Response({'ret_code': 3006, 'message': u'产品投资期限输入不合法'})

        try:
            if float(rate_min) > float(rate_max):
                return Response({'ret_code': 3007, 'message': u'产品投资最高收益率不允许小于最低收益率'})
        except:
            return Response({'ret_code': 3008, 'message': u'产品投资收益率输入不合法'})

        try:
            plan = AutomaticPlan.objects.filter(user=request.user)
            if plan.exists():
                plan = plan.first()
            else:
                plan = AutomaticPlan()
                plan.user = request.user

            plan.amounts_auto = Decimal(amounts_auto)
            plan.period_min = int(period_min)
            plan.period_max = int(period_max)
            plan.rate_min = int(rate_min)
            plan.rate_max = int(rate_max)
            plan.is_used = True if is_used else False

            plan.save()

            """
            # 停止这个入口，从watch进入自动投标
            if plan.is_used:
                automatic_trade.apply_async(kwargs={
                    "plan_id": plan.id,
                })
                pass
            """

            return Response({
                'ret_code': 0,
                'message': u'自动投标计划设置成功'
            })
        except:
            return Response({'ret_code': 3009, 'message': u'用户设置自动投标计划失败'})


# class CjdaoApiView(APIView):
#
#     """
#         财经道入口
#     """
#
#     permission_classes = ()
#
#     def get(self, request):
#         uaccount = request.GET.get('uaccount')
#         phone = request.GET.get('phone')
#         companyid = request.GET.get('companyid')
#         thirdproductid = request.GET.get('thirdproductid')
#
#         user = CjdaoUtils.get_wluser_by_phone(phone)
#
#         cjdaoinfo = {
#             'uaccount': uaccount,
#             'companyid': companyid,
#             'usertype': 0,
#         }
#         # 保存到 session
#         request.session['cjdaoinfo'] = cjdaoinfo
#
#         if thirdproductid:
#             try:
#                 p2p = P2PProduct.objects.select_related('activity').get(pk=int(thirdproductid), hide=False)
#             except P2PProduct.DoesNotExist:
#                 raise Http404(u'您查找的产品不存在')
#
#             request.session.get('cjdaoinfo').update(thirdproductid=int(thirdproductid))
#
#             if user:
#                 request.session.get('cjdaoinfo').update(usertype=1)
#                 return render_to_response('cjdao_login_product.jade', {'p2p': p2p, 'phone': phone})
#             else:
#                 return render_to_response('cjdao_register_product.jade', {'p2p': p2p, 'phone': phone})
#         else:
#
#             if user:
#                 request.session.get('cjdaoinfo').update(usertype=1)
#                 return render_to_response('cjdao_login.jade', {'uaccount': uaccount, 'phone': phone})
#             else:
#                 return render_to_response('cjdao_register.jade', {'uaccount': uaccount, 'phone': phone})
#
#
#
#
#
#
#
#
#
#

