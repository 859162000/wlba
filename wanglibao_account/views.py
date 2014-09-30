# encoding: utf-8
import datetime
import logging
import json
import math
from django.contrib import auth
from django.contrib.auth import login as auth_login
from django.db.models import Q, Sum, F
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed, Http404
from django.shortcuts import resolve_url
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from registration.views import RegistrationView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from forms import EmailOrPhoneRegisterForm, ResetPasswordGetIdentifierForm, IdVerificationForm
from marketing.utils import set_promo_user
from shumi_backend.exception import FetchException, AccessException
from shumi_backend.fetch import UserInfoFetcher
from utils import detect_identifier_type, create_user, generate_contract
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_account.forms import EmailOrPhoneAuthenticationForm
from wanglibao_account.serializers import UserSerializer
from wanglibao_buy.models import TradeHistory, BindBank, FundHoldInfo, DailyIncome
from wanglibao_p2p.models import P2PRecord, P2PEquity, ProductAmortization, UserAmortization
from wanglibao_pay.models import Card, Bank, PayInfo
from wanglibao_sms.utils import validate_validation_code, send_validation_code
from wanglibao_account.models import VerifyCounter
from rest_framework.permissions import IsAuthenticated
from wanglibao.const import ErrorNumber
from wanglibao_account.utils import verify_id


logger = logging.getLogger(__name__)

User = get_user_model()


class RegisterView (RegistrationView):
    template_name = "register.jade"
    form_class = EmailOrPhoneRegisterForm

    def register(self, request, **cleaned_data):
        nickname = cleaned_data['nickname']
        password = cleaned_data['password']
        identifier = cleaned_data['identifier']

        user = create_user(identifier, password, nickname)

        set_promo_user(request, user)

        auth_user = authenticate(identifier=identifier, password=password)
        auth.login(request, auth_user)
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
                users = User.objects.filter(wanglibaouserprofile__phone=identifier, wanglibaouserprofile__phone_verified=True)

            # There should be at most one user found
            assert len(users) <= 1

            if len(users) == 0:
                return HttpResponse(u"找不到该用户", status=400)
            else:
                view = PasswordResetValidateView()
                view.request = request
                if identifier_type == 'phone':
                    send_validation_code(identifier)
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
    user_email = get_user_model().objects.get(pk=user_id).email

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
    user_phone = get_user_model().objects.get(pk=user_id).wanglibaouserprofile.phone
    phone_number = user_phone.strip()

    status, message = send_validation_code(phone_number)

    return HttpResponse(
        str({"message": message}), status=status)


def validate_phone_code(request):
    logger.info("Enter validate_phone_code")
    validate_code = request.POST['validate_code']
    user_id = request.session['user_to_reset']
    user_phone = get_user_model().objects.get(pk=user_id).wanglibaouserprofile.phone
    phone_number = user_phone.strip()

    status, message = validate_validation_code(phone_number, validate_code)
    if status == 200:
        logger.debug("Phone code validated")
        request.session['phone_validated_time'] = (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds()
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
        user = get_user_model().objects.get(pk=user_id)

        assert('phone_validated_time' in request.session)
        last_validated_time = request.session['phone_validated_time']
        assert(last_validated_time != 0)

        if (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds() - last_validated_time < 30 * 60:
            user.set_password(password1)
            user.save()
            return HttpResponse(u'密码修改成功', status=200)

        else:
            return HttpResponse(u'验证超时，请重新验证', status=400)


class UserViewSet(PaginatedModelViewSet):
    model = get_user_model()
    serializer_class = UserSerializer
    permission_classes = IsAdminUser,


class AccountHome(TemplateView):
    template_name = 'account_home.jade'

    def get_context_data(self, **kwargs):
        message = ''
        user = self.request.user

        mode = 'p2p'
        fund_hold_info = []
        if self.request.path.rstrip('/').split('/')[-1] == 'fund':
            mode = 'fund'
            fund_hold_info = FundHoldInfo.objects.filter(user__exact=user)


        # Followings for p2p
        # p2p_equities = P2PEquity.objects.filter(user=user).filter(~Q(product__status=u"已完成")).select_related('product')

        p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
            u'已完成', u'满标待打款',u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
        ]).select_related('product')

        amortizations = ProductAmortization.objects.filter(product__in=[e.product for e in p2p_equities], settled=False).prefetch_related("subs")

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

        return {
            'message': message,

            'p2p_equities': p2p_equities,
            'amortizations': amortizations,
            'p2p_product_amortization': p2p_product_amortization,
            'p2p_unpay_principle': unpayed_principle,
            'margin_withdrawing': user.margin.withdrawing,
            'margin_freeze': user.margin.freeze,
            'fund_hold_info':fund_hold_info,
            'p2p_total_asset': p2p_total_asset,
            'total_asset': total_asset,

            'mode': mode
        }


class AccountHomeAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        user=request.user

        p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
            u'已完成', u'满标待打款',u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
        ]).select_related('product')



        unpayed_principle = 0
        p2p_total_paid_interest = 0
        p2p_total_unpaid_interest = 0
        p2p_total_interest = 0
        for equity in p2p_equities:
            if equity.confirm:
                unpayed_principle += equity.unpaid_principal        # 待收本金
                p2p_total_paid_interest += equity.paid_interest     # 累积收益
                p2p_total_unpaid_interest += equity.unpaid_interest # 待收益
                p2p_total_interest += equity.total_interest         # 总收益

        p2p_margin = user.margin.margin             # P2P余额
        p2p_freeze = user.margin.freeze             # P2P投资中冻结金额
        p2p_withdrawing = user.margin.withdrawing   # P2P提现中冻结金额
        p2p_unpayed_principle = unpayed_principle   # P2P待收本金

        p2p_total_asset = p2p_margin + p2p_freeze + p2p_withdrawing + p2p_unpayed_principle

        fund_hold_info = FundHoldInfo.objects.filter(user__exact=user)
        fund_total_asset = 0
        if fund_hold_info.exists():
            for hold_info in fund_hold_info:
                fund_total_asset += hold_info.current_remain_share + hold_info.unpaid_income

        today = timezone.datetime.today()
        total_income = DailyIncome.objects.filter(user=user).aggregate(Sum('income'))['income__sum'] or 0
        fund_income_week = DailyIncome.objects.filter(user=user, date__gt=today+datetime.timedelta(days=-8)).aggregate(Sum('income'))['income__sum'] or 0
        fund_income_month = DailyIncome.objects.filter(user=user, date__gt=today+datetime.timedelta(days=-31)).aggregate(Sum('income'))['income__sum'] or 0

        res = {
            'total_asset': float(p2p_total_asset + fund_total_asset),      # 总资产
            'p2p_total_asset': float(p2p_total_asset),                    # p2p总资产
            'p2p_margin': float(p2p_margin),                              # P2P余额
            'p2p_freeze': float(p2p_freeze),                              # P2P投资中冻结金额
            'p2p_withdrawing': float(p2p_withdrawing),                   # P2P提现中冻结金额
            'p2p_unpayed_principle': float(p2p_unpayed_principle),        # P2P待收本金
            'p2p_total_unpaid_interest': float(p2p_total_unpaid_interest),  # p2p总待收益
            'p2p_total_paid_interest': float(p2p_total_paid_interest),    # P2P总累积收益
            'p2p_total_interest': float(p2p_total_interest),              # P2P总收益

            'fund_total_asset': float(fund_total_asset),                   # 基金总资产
            'fund_total_income': float(total_income),                     # 基金累积收益
            'fund_income_week': float(fund_income_week),                   # 基金近一周收益(元)
            'fund_income_month': float(fund_income_month),                 # 基金近一月收益(元)

        }

        return Response(res)


class AccountP2PRecordAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        user=request.user
        # p2p_equities = P2PEquity.objects.filter(user=user).all().select_related('product')
        p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
            u'已完成', u'满标待打款',u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
        ]).select_related('product')

        page = request.GET.get('page', 0)
        try:
            page = int(page)
            if page < 0:
                return Response({ "detail": "Query String must be a number." }, status=404)
        except:
            return Response({ "detail": "Query String must be a number." }, status=404)

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
                    'equity_created_at':  timezone.localtime(equity.created_at).strftime("%Y-%m-%d %H:%M:%S"),          # 投标时间
                    'equity_product_short_name': equity.product.short_name,                                             # 产品名称
                    'equity_product_expected_earning_rate': equity.product.expected_earning_rate,                       # 年化收益(%)
                    'equity_product_period': equity.product.period,                                                     # 产品期限(月)*
                    'equity_equity': float(equity.equity),                                                                     # 用户所持份额(投资金额)
                    'equity_product_display_status': equity.product.display_status,                                     # 状态
                    'equity_term': equity.term,                                                                         # 还款期
                    'equity_product_amortization_count': equity.product.amortization_count,                             # 还款期数
                    'equity_paid_interest': float(equity.paid_interest),                                                       # 单个已经收益
                    'equity_total_interest': float(equity.total_interest),                                                     # 单个预期收益
                    'equity_contract': 'https://%s/accounts/p2p/contract/%s/' % (request.get_host(), equity.product.id), # 合同
                    'product_id': equity.product_id
            } for equity in p2p_equities]

        if int(page) != 0:
            res = {
                'total_counts': p2p_equities.paginator.count,                                               # 总条目数
                'total_page': int(math.ceil(p2p_equities.paginator.count / float(p2p_equities.paginator.per_page))),        # 总页数
                'per_page_number': p2p_equities.paginator.per_page,                                         # 每页显示条数
                'pre_page': p2p_equities.previous_page_number() if p2p_equities.has_previous() else None,   # 前一页页码
                'next_page': p2p_equities.next_page_number() if p2p_equities.has_next() else None,          # 后一页页码
                'p2p_records': p2p_records,
            }
        else:
            res = p2p_records
        return Response(res)


class AccountFundRecordAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        user=request.user
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
                'fund_fund_name': fund.fund_name,                               # 基金产品名称
                'fund_current_remain_share': float(fund.current_remain_share),         # 当前份额余额
                'fund_unpaid_income': float(fund.unpaid_income),                       # 未付收益
                'fund_code': fund.fund_code,                                    # 基金代码
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
        user=request.user

        p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
            u'已完成', u'满标待打款',u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
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

            'p2p_total_asset': float(p2p_total_asset),                     # 总资产
            'p2p_margin': float(p2p_margin),                               # P2P余额
            'p2p_freeze': float(p2p_freeze),                               # P2P投资中冻结金额
            'p2p_withdrawing': float(p2p_withdrawing),                     # P2P提现中冻结金额
            'p2p_unpayed_principle': float(p2p_unpayed_principle),         # P2P待收本金
            'p2p_total_unpaid_interest':float(p2p_total_unpaid_interest),  # p2p总待收益
            'p2p_total_paid_interest': float(p2p_total_paid_interest),     # P2P总累积收益
            'p2p_total_interest': float(p2p_total_interest),               # P2P总收益

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
        fund_income_week = DailyIncome.objects.filter(user=user, date__gt=today+datetime.timedelta(days=-8)).aggregate(Sum('income'))['income__sum'] or 0
        fund_income_month = DailyIncome.objects.filter(user=user, date__gt=today+datetime.timedelta(days=-31)).aggregate(Sum('income'))['income__sum'] or 0

        res = {
            'fund_total_asset': float(fund_total_asset),                   # 基金总资产
            'fund_total_income': float(total_income),                      # 基金累积收益
            'fund_income_week': float(fund_income_week),                   # 基金近一周收益(元)
            'fund_income_month': float(fund_income_month),                 # 基金近一月收益(元)
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
        fund_income_week = DailyIncome.objects.filter(user=user, date__gt=today+datetime.timedelta(days=-8)).aggregate(Sum('income'))['income__sum'] or 0
        fund_income_month = DailyIncome.objects.filter(user=user, date__gt=today+datetime.timedelta(days=-31)).aggregate(Sum('income'))['income__sum'] or 0

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
            "message": message
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
        return {
            "trade_records": trade_records
        }


class AccountTransactionDeposit(TemplateView):
    template_name = 'account_transaction_deposit.jade'

    def get_context_data(self, **kwargs):
        pay_records = PayInfo.objects.filter(user=self.request.user, type=PayInfo.DEPOSIT)
        pager = Paginator(pay_records, 20)
        page = self.request.GET.get('page')
        if not page:
            page = 1
        pay_records = pager.page(page)
        return {
            "pay_records": pay_records
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
            "pay_records": pay_records
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
            "message": message
        }


class ResetPasswordAPI(APIView):
    permission_classes = ()

    def post(self, request):
        password = request.DATA.get('new_password')
        identifier = request.DATA.get('identifier')
        validate_code = request.DATA.get('validate_code')

        if password is None:
            return Response({
                'message': u'缺少new_password这个字段'
            }, status=400)
        else:
            password = password.strip()

        if identifier is None:
            return Response({
                'message': u'缺少identifier这个字段'
            }, status=400)

        if validate_code is None:
            return Response({
                'message': u'缺少validate_code'
            }, status=400)

        identifier_type = detect_identifier_type(identifier)

        if identifier_type == 'phone':
            user = get_user_model().objects.get(wanglibaouserprofile__phone=identifier)
        else:
            return Response({
                'message': u'请输入手机号码'
            }, status=400)

        status, message = validate_validation_code(identifier, validate_code)
        if status == 200:
            user.set_password(password)
            user.save()
            return Response({
                'message': u'修改成功'
            })
        else:
            return Response({
                'message': u'验证码验证失败'
            }, status=400)


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
        return HttpResponseNotAllowed()


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

                user = create_user(identifier, password, nickname)
                set_promo_user(request, user)
                auth_user = authenticate(identifier=identifier, password=password)
                auth.login(request, auth_user)
                return HttpResponse(messenger('done', user=request.user))
                # return HttpResponseRedirect("/accounts/id_verify/")
            else:
                return HttpResponseForbidden(messenger(form.errors))
        else:
            return HttpResponseForbidden('not valid ajax request')
    else:
        return HttpResponseNotAllowed()


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
        user.wanglibaouserprofile.save()

        return super(IdVerificationView, self).form_valid(form)


class P2PAmortizationView(TemplateView):
    template_name = 'p2p_amortization_plan.jade'

    def get_context_data(self, **kwargs):
        product_id = kwargs['product_id']

        equity = P2PEquity.objects.filter(user=self.request.user, product_id=product_id).prefetch_related('product').first()

        amortizations = UserAmortization.objects.filter(user=self.request.user, product_amortization__product_id=product_id)
        return {
            'equity': equity,
            'amortizations': amortizations
        }

class P2PAmortizationAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, **kwargs):
        user = request.user
        product_id = kwargs['product_id']
        equity = P2PEquity.objects.filter(user=user, product_id=product_id).prefetch_related('product').first()
        amortizations = UserAmortization.objects.filter(user=self.request.user, product_amortization__product_id=product_id)

        amortization_record = [{
                'amortization_term_date': timezone.localtime(amortization.term_date).strftime("%Y-%m-%d %H:%M:%S"),                       # 还款时间
                'amortization_principal': float(amortization.principal),                      # 本金
                'amortization_amount_interest': float(amortization.interest),                 # 利息
                'amortization_amount': float(amortization.principal + amortization.interest), # 总记
            } for amortization in amortizations ]

        res = {
            'equity_product_short_name': equity.product.short_name,                     # 还款标题
            'equity_product_serial_number': equity.product.serial_number,               # 还款计划编号
            'amortization_record': amortization_record

        }
        return Response(res)


@login_required
def user_product_contract(request, product_id):
    equity = P2PEquity.objects.filter(user=request.user, product_id=product_id).prefetch_related('product').first()

    try:
        f = equity.contract
        lines = f.readlines()
        f.close()
        return HttpResponse("\n".join(lines))
    except ValueError, e:
        raise Http404


@login_required
def test_contract(request, equity_id):
    equity = P2PEquity.objects.filter(id=equity_id).prefetch_related('product').first()
    return HttpResponse(generate_contract(equity, 'hongmu_template.jade'))


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
        user.wanglibaouserprofile.save()

        return super(IdVerificationView, self).form_valid(form)


class AdminIdVerificationView(TemplateView):
    template_name = 'admin_verify_id.jade'


class IdValidate(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        user = self.request.user
        name = request.DATA.get("name", "")
        id_number = request.DATA.get("id_number", "")
        verify_counter, created = VerifyCounter.objects.get_or_create(user=user)

        if verify_counter.count >= 3:
            return Response({
                                "message": u"验证次数超过三次，请联系客服进行人工验证",
                                "error_number": ErrorNumber.try_too_many_times
                            }, status=400)

        verify_record, error = verify_id(name, id_number)

        verify_counter.count = F('count') + 1
        verify_counter.save()

        if error or not verify_record.is_valid:
            return Response({
                                "message": u"验证失败，拨打客服电话进行人工验证",
                                "error_number": ErrorNumber.unknown_error
                            }, status=400)

        user.wanglibaouserprofile.id_number = id_number
        user.wanglibaouserprofile.name = name
        user.wanglibaouserprofile.id_is_valid = True
        user.wanglibaouserprofile.save()

        return Response({
                            "validate": True
                        }, status=200)
