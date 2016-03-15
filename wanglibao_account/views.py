# encoding: utf-8
import datetime
from wanglibao_redpack.models import RedPackEvent, RedPack, RedPackRecord
from wanglibao_redpack import backends as redpack_backends
import logging
import json
import math
import random
import urllib

from random import randint
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
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed, Http404, HttpResponseRedirect
from django.shortcuts import resolve_url, render_to_response
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, View
from django.db import transaction
from registration.views import RegistrationView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from forms import EmailOrPhoneRegisterForm, LoginAuthenticationNoCaptchaForm,\
    ResetPasswordGetIdentifierForm, IdVerificationForm, TokenSecretSignAuthenticationForm,ManualModifyPhoneForm
from marketing.models import IntroducedBy, Channels, Reward, RewardRecord
from marketing.utils import set_promo_user, local_to_utc, get_channel_record
from marketing import tools
from wanglibao_sms.tasks import send_messages
from wanglibao_sms import messages as sms_messages
from shumi_backend.exception import FetchException, AccessException
from shumi_backend.fetch import UserInfoFetcher
from wanglibao import settings
from wanglibao_account.cooperation import CoopRegister
from wanglibao_account.utils import detect_identifier_type, create_user, generate_contract, update_coop_order
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_account import third_login, backends as account_backends, message as inside_message
from wanglibao_account.serializers import UserSerializer
from wanglibao_buy.models import TradeHistory, BindBank, FundHoldInfo, DailyIncome
from wanglibao_p2p.models import P2PRecord, P2PEquity, ProductAmortization, UserAmortization, Earning, \
    AmortizationRecord, P2PProductContract, P2PProduct, P2PEquityJiuxian, AutomaticPlan, AutomaticManager
from wanglibao_pay.models import Card, Bank, PayInfo
from wanglibao_sms.utils import validate_validation_code, send_validation_code, send_rand_pass
from wanglibao_account.models import VerifyCounter, Binding, Message, UserAddress, \
    UserThreeOrder, ManualModifyPhoneRecord, SMSModifyPhoneRecord
from rest_framework.permissions import IsAuthenticated
from wanglibao.const import ErrorNumber
from wanglibao.templatetags.formatters import safe_phone_str
from order.models import Order
from wanglibao_announcement.utility import AnnouncementAccounts
from django.template.defaulttags import register
from wanglibao_p2p.keeper import EquityKeeperDecorator
from order.utils import OrderHelper
from wanglibao_rest import utils
from wanglibao_activity.models import ActivityRecord
from aes import Crypt_Aes
from misc.models import Misc
from wanglibao_activity.models import Activity
from wanglibao_reward.models import WanglibaoUserGift, WanglibaoActivityGift
from wanglibao.settings import AMORIZATION_AES_KEY
from wanglibao_anti.anti.anti import AntiForAllClient
from wanglibao_account.utils import get_client_ip
# import requests
from wanglibao_margin.models import MarginRecord
from experience_gold.models import ExperienceAmortization, ExperienceEventRecord, ExperienceProduct
from wanglibao_pay.fee import WithdrawFee
from wanglibao_account import utils as account_utils
from wanglibao_rest.common import DecryptParmsAPIView
from wanglibao_sms.models import PhoneValidateCode
from wanglibao_account.forms import verify_captcha
from wanglibao_profile.models import WanglibaoUserProfile


logger = logging.getLogger(__name__)
logger_anti = logging.getLogger('wanglibao_anti')


class RegisterView(RegistrationView):
    template_name = "register_new.jade"
    form_class = EmailOrPhoneRegisterForm

    def register(self, request, **cleaned_data):
        """
            modified by: Yihen@20150812
            descrpition: if(line96~line97)的修改，针对特定的渠道延迟返积分、发红包等行为，防止被刷单
        """
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
        device = utils.split_ua(request)
        if not AntiForAllClient(request).anti_delay_callback_time(user.id, device):
            tools.register_ok.apply_async(kwargs={"user_id": user.id, "device": device})

        account_backends.set_source(request, auth_user)
        return user

    def get_success_url(self, request=None, user=None):
        if request.GET.get('next'):
            return request.GET.get('next')
        return '/accounts/login/'

    def get_context_data(self, **kwargs):

        sign = self.request.GET.get('sign', None)
        promo_token = self.request.GET.get('promo_token', None)

        # sign = urllib.urlencode(self.request.GET.get('sign', None))

        context = super(RegisterView, self).get_context_data(**kwargs)
        context.update({
            'next': self.request.GET.get('next', '/accounts/login/')
        })

        if sign and (promo_token == 'csai' or promo_token == 'xicai'):

            try:
                from wanglibao_account.cooperation import get_xicai_user_info
                key = settings.XICAI_CLIENT_SECRET[0:8]
                data = get_xicai_user_info(key, sign)
                phone = data['phone']
            except Exception, e:
                print 'get phone error, ', e
                phone = None

            if phone:
                context.update({
                    'phone': phone,
                })

        return context


# AES 加解密
# from Crypto.Cipher import AES
# import base64
#
# BS = AES.block_size
# pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
# unpad = lambda s: s[0:-ord(s[-1])]
#
# result = 'bAqCOs5Ox10kmcKKn7n47lDqljwBmKbHAtuWf0pkLqu7XbNaJOCXVEVJ9PRqIC5LiiB0MsbvjOEU+eIFWRSmaw=='
# all_the_text1 = base64.b64decode(result)
#
# cipher2 = AES.new(b'https://jrjia.cn')
# decrypted2 = unpad(cipher2.decrypt(all_the_text1))
# ecrypted = cipher2.encrypt(pad('{"src":"jrjia","reqId":"31646132","prodId":"1","mobile":"11811849324"}'))
# sign = base64.b64encode(ecrypted)


class JrjiaAutoRegisterView(APIView):
    """
    author： Zhoudong
    金融加 自动注册， 保存到 introduceby 表里。 之前需要添加金融加渠道。
    """

    permission_classes = ()

    def get_context_data(self):

        # key = 'jrjia.cn'
        key = 'https://jrjia.cn'
        src = self.request.GET.get('src', None)
        sign = self.request.GET.get('sign', None)

        if ' ' in sign:
            sign = sign.replace(' ', '+')

        if src == 'jrjia':
            # 解密
            import base64
            from Crypto.Cipher import AES

            decryptor = AES.new(key, AES.MODE_ECB)
            try:
                base_str = base64.b64decode(sign)
                sign_args = eval(decryptor.decrypt(base_str).split('}')[0] + '}')
            except Exception, e:
                sign = urllib.unquote(sign)
                base_str = base64.b64decode(sign)
                sign_args = eval(decryptor.decrypt(base_str).split('}')[0] + '}')

            context = {}
            context.update(sign_args)

            host = self.request.get_host()
            try:
                next_url = 'http://' + '{}/p2p/detail/{}/'.format(host, sign_args['prodId'])
            except Exception, e:
                print 'args error: {}'.format(e)
                next_url = '/'
            context.update({
                'next': next_url
            })

            return context

    def get(self, request):
        """
        :param request:
        :return:
        """
        args = self.get_context_data()
        redirect_url = args['next']

        try:
            source = args['src']
            password = str(random.randint(100000, 999999))
            identifier = args['mobile']
            req_id = args['reqId']
            nickname = identifier
        except Exception, e:
            print 'args get error: {}'.format(e)
            return HttpResponseRedirect(redirect_url)

        # 用户已存在， 返回
        if User.objects.filter(wanglibaouserprofile__phone=identifier).first():
            return HttpResponseRedirect(redirect_url)

        user = create_user(identifier, password, nickname)
        channel = Channels.objects.get(code=source)

        # 当用户不存在， 添加到binding 表（自带reqId）
        Binding.objects.get_or_create(user=user, btype=source, bid=req_id)
        # 邀请关系表
        IntroducedBy.objects.get_or_create(user=user, channel=channel)

        auth_user = authenticate(identifier=identifier, password=password)
        auth.login(request, auth_user)

        device = utils.split_ua(request)
        if not AntiForAllClient(request).anti_delay_callback_time(user.id, device):
            tools.register_ok.apply_async(kwargs={"user_id": user.id, "device": device})

        # send message for the user.
        send_rand_pass(identifier, password)

        account_backends.set_source(request, auth_user)

        return HttpResponseRedirect(redirect_url)


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


class PasswordCheckView(DecryptParmsAPIView):
    permission_classes = ()
    def post(self, request, **kwargs):
        identifier = self.params.get("identifier", "")
        password = self.params.get("password", "")
        # identifier = request.DATA.get("identifier", "")
        # password = request.DATA.get("password", "")

        if not identifier or not password:
            return Response({"token":False, "message":u"登录密码错误，请重试"})

        user = authenticate(identifier=identifier, password=password)

        if not user:
            return Response({"token":False, "message":u"登录密码错误，请重试"})
        if not user.is_active:
            return Response({"token":False, "message":u"用户已被关闭"})
        if user.wanglibaouserprofile.frozen:
            return Response({"token":False, "message":u"用户已被冻结"})

        return Response({'token':True, 'message':u'用户认证成功'})


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
                return HttpResponse(u"非法请求", status=400)
                # users = User.objects.filter(email=identifier, is_active=True)
            elif identifier_type == 'phone':
                users = User.objects.filter(wanglibaouserprofile__phone=identifier,
                                            wanglibaouserprofile__phone_verified=True)

            # There should be at most one user found
            assert len(users) <= 1

            if len(users) == 0:
                return HttpResponse(u"找不到该用户", status=400)
            else:
                try:
                    # 清除session验证时间
                    del request.session['phone_validated_time']

                    # 如果session中已经有用户id,则验证已有的和当前提交的是否一致,不一致则认为是非法操作
                    if request.session['user_to_reset']:
                        session_user_id = request.session['user_to_reset']
                        if session_user_id != users[0].id:
                            return HttpResponse(u"非法请求", status=400)
                except KeyError:
                    pass

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
    user_phone = User.objects.get(pk=user_id).wanglibaouserprofile.phone
    phone_number = user_phone.strip()

    status, message = send_validation_code(phone_number, ip=utils.get_client_ip(request))

    return HttpResponse(
        str({"message": message}), status=status)


def validate_phone_code(request):
    logger.info("Enter validate_phone_code")
    validate_code = request.POST['validate_code']
    user_id = request.session['user_to_reset']
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
        user = User.objects.get(pk=user_id)

        assert ('phone_validated_time' in request.session)
        last_validated_time = request.session['phone_validated_time']
        assert (last_validated_time != 0)

        # 缩短session失效时间
        if (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds() - last_validated_time < 10 * 60:
            user.set_password(password1)
            user.save()
            
            # 清除session
            try:
                del request.session['phone_validated_time']
                del request.session['user_to_reset']
            except KeyError:
                pass

            return HttpResponse(u'密码修改成功', status=200)

        else:
            return HttpResponse(u'验证超时，请重新验证', status=400)


class UserViewSet(PaginatedModelViewSet):
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
        if self.request.path.rstrip('/').split('/')[-1] == 'experience':
            mode = 'experience'

        p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
            u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
        ]).select_related('product')

        # author: hetao; datetime: 2014.10.30; description: 加上活动所得收益
        earnings = Earning.objects.select_related('product__activity').filter(user=user)

        earning_map = {earning.product_id: earning for earning in earnings}

        unpayed_principle = 0
        for equity in p2p_equities:
            if equity.confirm:
                unpayed_principle += equity.unpaid_principal

        p2p_total_asset = user.margin.margin + user.margin.freeze + user.margin.withdrawing + unpayed_principle

        total_asset = p2p_total_asset

        result = []

        if mode == 'p2p':
            for equity in p2p_equities:
                obj = {"equity": equity}
                if earning_map.get(equity.product_id):
                    obj["earning"] = earning_map.get(equity.product_id)

                result.append(obj)

        now = timezone.now()
        experience_amount = 0
        paid_interest = unpaid_interest = 0

        experience_product = ExperienceProduct.objects.filter(isvalid=True).first()
        experience_record = ExperienceEventRecord.objects.filter(user=user, apply=False, event__invalid=False)\
            .filter(event__available_at__lt=now, event__unavailable_at__gt=now).aggregate(Sum('event__amount'))
        if experience_record.get('event__amount__sum'):
            experience_amount = experience_record.get('event__amount__sum')

        experience_amortization = ExperienceAmortization.objects.filter(user=user)\
            .select_related('product').order_by('-created_time')
        if experience_amortization:
            paid_interest = reduce(lambda x, y: x + y,
                                   [e.interest for e in experience_amortization if e.settled is True], 0)
            unpaid_interest = reduce(lambda x, y: x + y,
                                     [e.interest for e in experience_amortization if e.settled is False], 0)

        total_experience_amount = float(experience_amount) + float(paid_interest) + float(unpaid_interest)
        experience_account = {
            'total_experience_amount': total_experience_amount,
            'experience_amount': float(experience_amount),
            'paid_interest': paid_interest,
            'unpaid_interest': unpaid_interest,
            'experience_amortization': experience_amortization,
            'product': experience_product,
        }

        return {
            'message': message,
            'result': result,
            'p2p_unpay_principle': unpayed_principle,
            'margin_withdrawing': user.margin.withdrawing,
            'margin_freeze': user.margin.freeze,
            'p2p_total_asset': p2p_total_asset,
            'total_asset': total_asset,
            'mode': mode,
            'experience_amortization': experience_amortization,
            'experience_account': experience_account,
            'announcements': AnnouncementAccounts,
        }


class AccountHomeAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        user = request.user

        p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
            u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
        ]).select_related('product')

        start_utc = local_to_utc(datetime.datetime.now(), 'min')
        yesterday_start = start_utc - datetime.timedelta(days=1)
        yesterday_end = yesterday_start + datetime.timedelta(hours=23, minutes=59, seconds=59)

        unpayed_principle = 0
        p2p_total_paid_interest = 0
        p2p_total_unpaid_interest = 0
        p2p_total_interest = 0
        p2p_activity_interest = 0
        p2p_total_coupon_interest = 0
        p2p_total_paid_coupon_interest = 0
        p2p_total_unpaid_coupon_interest = 0
        p2p_income_today = 0
        p2p_income_yesterday = 0
        for equity in p2p_equities:
            if equity.confirm:
                unpayed_principle += equity.unpaid_principal  # 待收本金
                p2p_total_paid_interest += equity.pre_paid_interest  # 累积收益
                p2p_total_unpaid_interest += equity.unpaid_interest  # 待收益
                p2p_total_interest += equity.pre_total_interest  # 总收益
                p2p_total_coupon_interest += equity.pre_total_coupon_interest  # 加息券总收益
                p2p_total_paid_coupon_interest += equity.pre_paid_coupon_interest  # 加息券已收总收益
                p2p_total_unpaid_coupon_interest += equity.unpaid_coupon_interest  # 加息券待收总收益
                p2p_activity_interest += equity.activity_interest  # 活动收益

                # if equity.confirm_at >= start_utc:
                #     p2p_income_today += equity.pre_paid_interest
                #     p2p_income_today += equity.pre_paid_coupon_interest
                #     p2p_income_today += equity.activity_interest

        # 利息入账, 罚息入账, 活动赠送, 邀请赠送, 加息存入, 佣佣金存入, 全民淘金
        p2p_income_yesterday_other = MarginRecord.objects.filter(user=user)\
            .filter(create_time__gt=yesterday_start, create_time__lte=yesterday_end)\
            .filter(catalog__in=[u'利息入账', u'罚息入账', u'加息存入', u'佣金存入', u'全民淘金']).aggregate(Sum('amount'))

        if p2p_income_yesterday_other.get('amount__sum'):
            p2p_income_yesterday += p2p_income_yesterday_other.get('amount__sum')

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
                            date__gt=today + datetime.timedelta(days=-8)).aggregate(Sum('income'))['income__sum'] or 0
        fund_income_month = DailyIncome.objects.filter(user=user,
                            date__gt=today + datetime.timedelta(days=-31)).aggregate(Sum('income'))['income__sum'] or 0

        # 当月免费提现次数
        fee_config = WithdrawFee().get_withdraw_fee_config()
        free_times_per_month = int(fee_config['fee']['free_times_per_month'])
        withdraw_success_count = int(WithdrawFee().get_withdraw_count(user))
        withdraw_free_count = free_times_per_month - withdraw_success_count

        if withdraw_free_count <= 0:
            withdraw_free_count = 0

        res = {
            'total_asset': float(p2p_total_asset + fund_total_asset),  # 总资产
            'p2p_total_asset': float(p2p_total_asset),  # p2p总资产
            'p2p_margin': float(p2p_margin),  # P2P余额
            'p2p_freeze': float(p2p_freeze),  # P2P投资中冻结金额
            'p2p_withdrawing': float(p2p_withdrawing),  # P2P提现中冻结金额
            'p2p_unpayed_principle': float(p2p_unpayed_principle),  # P2P待收本金
            'p2p_total_unpaid_interest': float(p2p_total_unpaid_interest + p2p_total_unpaid_coupon_interest),  # p2p总待收益
            'p2p_total_paid_interest': float(p2p_total_paid_interest + p2p_activity_interest + p2p_total_paid_coupon_interest),  # P2P总累积收益
            'p2p_total_interest': float(p2p_total_interest + p2p_total_coupon_interest),  # P2P总收益

            'fund_total_asset': float(fund_total_asset),  # 基金总资产
            'fund_total_income': float(total_income),  # 基金累积收益
            'fund_income_week': float(fund_income_week),  # 基金近一周收益(元)
            'fund_income_month': float(fund_income_month),  # 基金近一月收益(元)

            'p2p_income_today': float(p2p_income_today),  # 今日收益
            'p2p_income_yesterday': float(p2p_income_yesterday),  # 昨日到账收益
            'withdraw_free_count': withdraw_free_count,  # 当月免费提现次数

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
                first_intro.append([safe_phone_str(users[user_id].phone), commission[user_id]['amount'], commission[user_id]['earning']])
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

        hikes = redpack_backends.get_hike_nums(request.user)
        amount = redpack_backends.get_hike_amount(request.user)
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
                           'equity_paid_interest': float(equity.pre_paid_interest),  # 单个已收收益
                           'equity_total_interest': float(equity.pre_total_interest),  # 单个预期收益
                           'equity_paid_coupon_interest': float(equity.pre_paid_coupon_interest),  # 加息券单个已收收益
                           'equity_total_coupon_interest': float(equity.pre_total_coupon_interest),  # 加息券单个预期收益
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
        result = redpack_backends.list_redpack(user, 'all', device['device_type'], 0)
        red_packets = result['packages'].get(status, [])

        return {
            "red_packets": red_packets,
            "status": status
        }


class AccountCoupon(TemplateView):
    template_name = 'coupon_available.jade'

    def get_context_data(self, **kwargs):

        status = kwargs['status']
        if status not in ('used', 'unused', 'expires'):
            status = 'unused'

        user = self.request.user
        device = utils.split_ua(self.request)
        result = redpack_backends.list_redpack(user, 'all', device['device_type'], 0, 'coupon')
        coupons = result['packages'].get(status, [])

        return {
            "coupons": coupons,
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


class ResetPasswordAPI(DecryptParmsAPIView):
    permission_classes = ()

    def post(self, request):
        password = self.params.get('new_password', "")
        identifier = self.params.get('identifier', "")
        validate_code = self.params.get('validate_code', "")
        # password = request.DATA.get('new_password', "")
        # identifier = request.DATA.get('identifier', "")
        # validate_code = request.DATA.get('validate_code', "")

        identifier = identifier.strip()
        password = password.strip()
        validate_code = validate_code.strip()

        if not password or not identifier or not validate_code:
            return Response({'ret_code': 30002, 'message': u'信息输入不完整'})

        if not 6 <= len(password) <= 20:
            return Response({'ret_code': 30001, 'message': u'密码需要在6-20位之间'})

        identifier_type = detect_identifier_type(identifier)

        if identifier_type == 'phone':
            # user = get_user_model().objects.get(wanglibaouserprofile__phone=identifier)
            user = User.objects.get(wanglibaouserprofile__phone=identifier)
        else:
            return Response({'ret_code': 30003, 'message': u'请输入手机号码'})

        status, message = validate_validation_code(identifier, validate_code)
        if status == 200:
            user.set_password(password)
            user.save()

            # 重置密码后将用户的错误登录次数清零
            user_profile = WanglibaoUserProfile.objects.get(user=user)
            user_profile.login_failed_count = 0
            user_profile.login_failed_time = timezone.now()
            user_profile.save()

            return Response({'ret_code': 0, 'message': u'修改成功'})
        else:
            # Modify by hb on 2015-12-02
            # return Response({'ret_code': 30004, 'message': u'验证码验证失败'})
            return Response({'ret_code': 30004, 'message': message})


class Third_login(View):
    def get(self, request, login_type):
        url = third_login.assem_params(login_type, request)
        return HttpResponseRedirect(url)


class Third_login_back(APIView):
    permission_classes = ()

    def get(self, request):
        result = third_login.login_back(request)
        return Response(result)


class ChangePasswordAPIView(DecryptParmsAPIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        # new_password = request.DATA.get('new_password', "").strip()
        # old_password = request.DATA.get('old_password', "").strip()
        # validate_code = request.DATA.get('validate_code', "").strip()
        new_password = self.params.get('new_password', "").strip()
        old_password = self.params.get('old_password', "").strip()
        validate_code = self.params.get('validate_code', "").strip()
        if not old_password or not new_password or not validate_code:
            return Response({'ret_code': 30041, 'message': u'信息输入不完整'})

        if not 6 <= len(new_password) <= 20:
            return Response({'ret_code': 30042, 'message': u'密码需要在6-20位之间'})

        user = request.user
        if not user.check_password(old_password):
            return Response({'ret_code': 30043, 'message': u'原密码错误'})

        status, message = validate_validation_code(user.wanglibaouserprofile.phone, validate_code)
        if status != 200:
            # Modify by hb 0n 2015-12-02
            # return Response({"ret_code": 30044, "message": u"验证码输入错误"})
            return Response({"ret_code": 30044, "message": message})

        user.set_password(new_password)
        user.save()
        # 重置密码后将用户的错误登录次数清零
        user_profile = WanglibaoUserProfile.objects.get(user=user)
        user_profile.login_failed_count = 0
        user_profile.login_failed_time = timezone.now()
        user_profile.save()

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
def ajax_login(request, authentication_form=LoginAuthenticationNoCaptchaForm):
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

from django import forms
from django.shortcuts import redirect
@sensitive_post_parameters()
@csrf_protect
@never_cache
def ajax_token_login(request, authentication_form=TokenSecretSignAuthenticationForm):
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
    """
        modified-1 by: Yihen@20150812
        descrpition: if(line1150~line1151)的修改，针对特定的渠道延迟返积分、发红包等行为，防止被刷单

        //////////////////////////

        modified-2 by: Yihen@20150818
        descrpition: if(line1154~line1156)的修改，web端在注册的时候，不需要再次验证图片验证码, code暂留，后期会加上这方面的逻辑
    """
    def messenger(message, user=None):
        res = dict()
        if user:
            res['nick_name'] = user.wanglibaouserprofile.nick_name
        res['message'] = message
        return json.dumps(res)

    def generate_random_password(length):
        if length < 0:
            raise Exception("生成随机密码的长度有误")

        random_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        password = ""
        index = 0
        while index < length:
            password += str(random_list[randint(0,len(random_list)-1)])
            index += 1
        return str(password)

    if request.method == "POST":
        channel = request.session.get(settings.PROMO_TOKEN_QUERY_STRING, "")    #add by Yihen@20150818; reason:第三方渠道处理的时候，会更改request中的信息
        if request.is_ajax():

            form = EmailOrPhoneRegisterForm(request.POST)
            if form.is_valid():
                nickname = form.cleaned_data['nickname']
                password = form.cleaned_data['password']
                identifier = form.cleaned_data['identifier']
                invitecode = form.cleaned_data['invitecode']
                user_type = form.cleaned_data.get('user_type', '0')

                if request.POST.get('IGNORE_PWD', '') and not password:
                    password = generate_random_password(6)

                if User.objects.filter(wanglibaouserprofile__phone=identifier).values("id"):
                    return HttpResponse(messenger('error'))

                user = create_user(identifier, password, nickname, user_type)
                if not user:
                    return HttpResponse(messenger('error'))

                if user_type == '3':
                    invitecode = 'qyzh'

                # 处理第三方渠道的用户信息
                CoopRegister(request).all_processors_for_user_register(user, invitecode)
                auth_user = authenticate(identifier=identifier, password=password)

                auth.login(request, auth_user)

                device = utils.split_ua(request)

                if not AntiForAllClient(request).anti_delay_callback_time(user.id, device, channel):
                    tools.register_ok.apply_async(kwargs={"user_id": user.id, "device": device})

                #  add by Yihen@20151020, 用户填写手机号不写密码即可完成注册, 给用户发短信,不要放到register_ok中去，保持原功能向前兼容
                if request.POST.get('IGNORE_PWD', ''):
                    send_messages.apply_async(kwargs={
                        "phones": [identifier, ],
                        "messages": [u'登录账户是：'+identifier+u'登录密码:'+password, ]
                    })

                    if channel == 'maimai':
                        dt = timezone.datetime.now()
                        redpack_event = RedPackEvent.objects.filter(invalid=False, name='maimai_redpack', give_start_at__lte=dt, give_end_at__gte=dt).first()
                        if redpack_event:
                            redpack_backends.give_activity_redpack(user, redpack_event, 'pc')

                    if channel == 'weixin_attention':
                        key = 'share_redpack'
                        shareconfig = Misc.objects.filter(key=key).first()
                        if shareconfig:
                            shareconfig = json.loads(shareconfig.value)
                            if type(shareconfig) == dict:
                                is_attention = shareconfig.get('is_attention', '')
                                attention_code = shareconfig.get('attention_code', '')

                        if is_attention:
                            activity = Activity.objects.filter(code=attention_code).first()
                            redpack = WanglibaoUserGift.objects.create(
                                identity=identifier,
                                activity=activity,
                                rules=WanglibaoActivityGift.objects.first(),#随机初始化一个值
                                type=1,
                                valid=0
                            )
                            dt = timezone.datetime.now()
                            redpack_event = RedPackEvent.objects.filter(invalid=False, name='weixin_atten_interest', give_start_at__lte=dt, give_end_at__gte=dt).first()
                            if redpack_event:
                                redpack_backends.give_activity_redpack(user, redpack_event, 'pc')
                                redpack.valid = 1
                                redpack.save()

                account_backends.set_source(request, auth_user)

                return HttpResponse(messenger('done', user=request.user))
            else:
                return HttpResponseForbidden(messenger(form.errors))
        else:
            return HttpResponseForbidden('not valid ajax request')
    else:
        return HttpResponseNotAllowed(["GET"])


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
            'amortization_term_date': timezone.localtime(amortization.term_date).strftime("%Y-%m-%d %H:%M:%S"),  # 还款时间
            'amortization_principal': float(amortization.principal),  # 本金
            'amortization_amount_interest': float(amortization.interest),  # 利息
            'amortization_amount': float(amortization.principal + amortization.interest + amortization.coupon_interest),  # 本息总和
            'amortization_coupon_interest': float(amortization.coupon_interest),  # 加息券利息
            'amortization_status': self._check_status(amortization.settled, amortization.settlement_time, amortization.term_date)
        } for amortization in amortizations]

        res = {
            'equity_product_short_name': equity.product.short_name,  # 还款标题
            'equity_product_serial_number': equity.product.serial_number,  # 还款计划编号
            'amortization_record': amortization_record

        }
        return Response(res)

    def _check_status(self, settled, settlement_time, term_date):
        if settled:
            if settlement_time.strftime('%Y-%m-%d') < term_date.strftime('%Y-%m-%d'):
                return u'提前回款'
            else:
                return u'已回款'
        else:
            return u'待回款'


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

def user_product_contract_kf(request):
    product_id = request.GET.get('product_id', "").strip()
    user_id = request.GET.get("user_id", "").strip()
    if not product_id.isdigit() or not user_id.isdigit():
        return Response({
            'message': u'参数错误',
            'error_number': ErrorNumber.param_error
        })
    user = User.objects.filter(id=user_id).get()
    if not user:
        return Response({
            'message': u'用户不存在',
            'error_number': ErrorNumber.param_error
        })
    equity = P2PEquity.objects.filter(user=user, product_id=product_id).prefetch_related('product').first()

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
        my_aes = Crypt_Aes(AMORIZATION_AES_KEY)
        result = my_aes.encrypt("\n".join(lines))
        # return HttpResponse(my_aes.decrypt(result))
        return HttpResponse(result)
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
        # add by ChenWeiBin@2010105
        if user.wanglibaouserprofile.utype == '3':
            return {"ret_code": 30056, "message": u"企业用户无法通过此方式认证"}

        user.wanglibaouserprofile.id_number = form.cleaned_data.get('id_number').strip()
        user.wanglibaouserprofile.name = form.cleaned_data.get('name').strip()
        user.wanglibaouserprofile.id_is_valid = True
        user.wanglibaouserprofile.id_valid_time = timezone.now()
        user.wanglibaouserprofile.save()

        return super(IdVerificationView, self).form_valid(form)


class AdminIdVerificationView(TemplateView):
    template_name = 'admin_verify_id.jade'


class AdminSendMessageView(TemplateView):
    template_name = "admin_send_message.jade"

    def get_context_data(self, **kwargs):
        flag = self.request.GET.get('flag', '')

        return {
            'flag': flag
        }

    def post(self, request):
        phones = request.POST.get("phones", "")
        title = request.POST.get("title", "")
        content = request.POST.get("content", "")
        mtype = request.POST.get("mtype", "activity")
        exchange_codes = request.POST.get("exchange_codes", "")
        flag = request.POST.get('flag', '')
        if not phones or not title or not content or not mtype:
            return self.render_to_response(
                {
                    "message": u"信息输入不完整"
                }
            )
        if flag and flag != 'different_batch':
            return self.render_to_response(
                {
                    "message": u"参数不正确"
                }
            )
        if flag and not exchange_codes:
            return self.render_to_response(
                {
                    "message": u"兑换码信息输入不完整"
                }
            )
        phone_list = phones.split('\r\n')
        phone_list = [phone for phone in phone_list if phone.strip() != ""]
        codes_list = exchange_codes.split('\r\n')
        codes_list = [code for code in codes_list if code.strip() != ""]
        if flag and len(phone_list) != len(codes_list):
            return self.render_to_response(
                {
                    "message": u"手机号码和兑换码的数量不一致"
                }
            )
        send_result = []
        code = ''
        for index, phone in enumerate(phone_list):
            user = User.objects.filter(wanglibaouserprofile__phone=phone).first()
            if not user:
                result = {
                    'phone': phone,
                    'status': 'not exist',
                    'message': u"用户不存在"
                }
                send_result.append(result)
                continue

            if flag == 'different_batch':
                from django.template import Template, Context
                code = codes_list[index]
                tmp_template = Template(content)
                content_result = tmp_template.render(Context({
                    'code': code
                }))
            else:
                content_result = content

            msg = msg_sms = ''
            # 发送理财券
            coupon_ids = request.POST.get("coupon_ids", "")
            if coupon_ids:
                now = timezone.now()
                coupon_ids_list = coupon_ids.split(",")
                coupon_ids_list = [cid for cid in coupon_ids_list if cid.strip() != ""]
                if coupon_ids_list:
                    for coupon_id in coupon_ids_list:
                        red_pack_event = RedPackEvent.objects.filter(invalid=False, id=coupon_id)\
                            .filter(give_start_at__lt=now, give_end_at__gt=now).first()
                        if red_pack_event:
                            redpack = RedPack.objects.filter(event=red_pack_event, status="unused").first()
                            if redpack:
                                give_pf = red_pack_event.give_platform
                                if give_pf == "all" or give_pf == 'pc':
                                    if redpack.token != "":
                                        redpack.status = "used"
                                        redpack.save()
                                    record = RedPackRecord()
                                    record.user = user
                                    record.redpack = redpack
                                    record.change_platform = 'pc'
                                    record.save()
                                    msg += u'id:{},成功;'.format(coupon_id)
                                else:
                                    msg += u'id:{},失败;'.format(coupon_id)
                        else:
                            msg += u'id:{},失败;'.format(coupon_id)

            # 发送短信
            content_sms = request.POST.get("content_sms", "")
            if content_sms:
                # 发送短信,功能推送id: 7
                # 直接发送短信内容
                from wanglibao_sms.send_php import PHPSendSMS
                PHPSendSMS().send_sms_msg_one(7, phone, 'phone', content_sms)
                # send_messages.apply_async(kwargs={
                #     'phones': [phone],
                #     'messages': [content_sms + sms_messages.SMS_STR_WX + sms_messages.SMS_SIGN_TD],
                #     'ext': 666,  # 营销类短信发送必须增加ext参数,值为666
                # })
                msg_sms += u'短信发送成功'

            # 发送站内信
            try:
                inside_message.send_one.apply_async(kwargs={
                    "user_id": user.id,
                    "title": title,
                    "content": content_result,
                    "mtype": mtype
                })

                result = {
                    'phone': "{}, {}".format(phone, code),
                    'status': 'success',
                    'message': u'站内信发送成功;' + msg + msg_sms
                }
            except False:
                result = {
                    'phone': phone,
                    'status': 'fail',
                    'message': u'站内信发送失败;' + msg + msg_sms
                }

            send_result.append(result)

        return self.render_to_response(
            {
                "message": u"发送结果如下:",
                "send_result": send_result,
                'flag': flag
            }
        )


#class IntroduceRelation(TemplateView):
#    template_name = 'introduce_add.jade'
#
#    def post(self, request):
#        user_phone = request.POST.get('user_phone', '').strip()
#        introduced_by_phone = request.POST.get('introduced_by_phone', '').strip()
#        bought_at = request.POST.get('bought_at', '').strip()
#        gift_send_at = request.POST.get('gift_send_at', '').strip()
#        try:
#            user = User.objects.get(wanglibaouserprofile__phone=user_phone)
#        except User.DoesNotExist:
#            return HttpResponse({
#                u"没有找到 %s 该记录" % user_phone
#            })
#        try:
#            introduced_by = User.objects.get(wanglibaouserprofile__phone=introduced_by_phone)
#        except User.DoesNotExist:
#            return HttpResponse({
#                u"没有找到 %s 该记录" % user_phone
#            })
#        try:
#            introduce = IntroducedBy.objects.get(user=user, introduced_by=introduced_by)
#        except IntroducedBy.DoesNotExist:
#            record = IntroducedBy()
#            record.introduced_by = introduced_by
#            record.user = user
#            if bought_at:
#                print(bought_at)
#                record.bought_at = bought_at
#            if gift_send_at:
#                print(gift_send_at)
#                record.gift_send_at = gift_send_at
#            record.created_by = request.user
#            record.save()
#            return HttpResponse({
#                u" %s与%s的邀请关系已经确定" % (user_phone, introduced_by)
#            })
#
#        return HttpResponse({
#            u" %s与%s的邀请关系已经存在" % (user_phone, introduced_by)
#        })
#
#    @method_decorator(permission_required('marketing.add_introducedby'))
#    def dispatch(self, request, *args, **kwargs):
#        """
#        Only user with change payinfo permission can call this view
#        """
#        return super(IntroduceRelation, self).dispatch(request, *args, **kwargs)


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
                address = UserAddress.objects.get(id=address_id, user=self.request.user)
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
            address = UserAddress.objects.get(id=address_id, user=self.request.user)
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
            address = UserAddress.objects.get(id=address_id, user=self.request.user)
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


class ThirdOrderApiView(APIView):
    """
    记录来自第三方回调的订单状态
    """

    permission_classes = ()

    def check_params_length(self, param, field_name):
        if len(param) <= UserThreeOrder._meta.get_field_by_name(field_name)[0].max_length:
            return True

    def check_params(self, request_no, result_code, msg):
        json_response = {}
        if request_no is None:
            json_response = {
                'ret_code': 20001,
                'message': u'request_no参数缺失'
            }
        elif not self.check_params_length(request_no, 'request_no'):
            json_response = {
                'ret_code': 20003,
                'message': u'request_no长度超出'
            }

        elif result_code is None:
            json_response = {
                'ret_code': 20004,
                'message': u'result_code参数缺失'
            }
        elif not self.check_params_length(result_code, 'result_code'):
            json_response = {
                'ret_code': 20006,
                'message': u'result_code长度超出'
            }

        elif not self.check_params_length(msg, 'msg'):
            json_response = {
                'ret_code': 20007,
                'message': u'result_code长度超出'
            }

        return json_response

    def is_trust_ip(self, trust_ip_list, request):
        if len(trust_ip_list) > 0 and get_client_ip(request) in trust_ip_list:
            return True

    def post(self, request, channel_code):
        if self.is_trust_ip(settings.TRUST_IP, request):
            if get_channel_record(channel_code):
                params = json.loads(request.POST)
                request_no = params.get('request_no', None)
                result_code = params.get('result_code', None)
                msg = params.get('message', '')
                json_response = self.check_params(request_no, result_code, msg)
                if not json_response:
                    json_response = update_coop_order(request_no, channel_code, result_code, msg)
            else:
                json_response = {
                    'ret_code': 10001,
                    'message': u'无效渠道码'
                }
        else:
            json_response = {
                'ret_code': 30001,
                'message': u'不受信任的来源！！！'
            }

        if channel_code == 'zgdx':
            return HttpResponse(json_response['ret_code'])
        else:
            return HttpResponse(json.dumps(json_response), content_type='application/json')


class ThirdOrderQueryApiView(APIView):
    """
    第三方订单查询接口
    """

    permission_classes = ()

    def get(self, request):
        params = getattr(request, request.method)
        channel_code = params.get('promo_token', None)
        if channel_code:
            order_query_fun = getattr(account_utils, '%s_order_query' % channel_code.lower(), None)
            if order_query_fun:
                json_response = order_query_fun(params)
            else:
                json_response = {
                    'ret_code': 50001,
                    'message': 'api error'
                }
                logger.error('%s_order_query not found' % channel_code.lower())
        else:
            json_response = {
                'ret_code': 10002,
                'message': u'渠道码缺失'
            }

        return HttpResponse(json.dumps(json_response), content_type='application/json')


class FirstPayResultView(TemplateView):
    template_name = 'register_three.jade'

    def get_context_data(self, **kwargs):
        first_pay_succeed = PayInfo.objects.filter(user=self.request.user, status=PayInfo.SUCCESS).exists()
        return {'first_pay_succeed': first_pay_succeed}


class IdentityInformationTemplate(TemplateView):
    template_name = ''

    def get_context_data(self, **kwargs):
        user = self.request.user
        profile = user.wanglibaouserprofile
        modify_phone_record = ManualModifyPhoneRecord.objects.filter(user=user).first()
        modify_phone_state = 0
        if modify_phone_record:
            if modify_phone_record.status == u'复审通过':
                modify_phone_state = 1
            if modify_phone_record.status in [u'待初审', u'初审待定', u'待复审']:
                modify_phone_state = 2
            if modify_phone_record.status in [u"初审驳回", u"复审驳回"]:
                modify_phone_state = 3
        card = Card.objects.filter(user=self.request.user, is_the_one_card=True)
        is_bind_card = card.exists()
        return {
            "phone": safe_phone_str(profile.phone),
            "id_is_valid": profile.id_is_valid,
            "trade_pwd": profile.trade_pwd != "",
            "modify_phone_state": modify_phone_state,
            'name': profile.name,
            "id_number": profile.id_number,
            "is_bind_card":is_bind_card
        }


class ValidateAccountInfoTemplate(TemplateView):
    template_name = ""

    def get_context_data(self, **kwargs):
        # cards = Card.objects.filter(user=self.request.user).filter(Q(is_bind_huifu=True)|Q(is_bind_kuai=True)|Q(is_bind_yee=True))
        card = Card.objects.filter(user=self.request.user, is_the_one_card=True)
        is_bind_card = card.exists()
        return {
            'is_bind_card': is_bind_card
        }


class ValidateAccountInfoAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = self.request.user
        profile = user.wanglibaouserprofile
        id_number = request.DATA.get('id_number', "").strip()
        params = request.DATA
        data = {}
        for k,v in params.iteritems():
            data[k]=v
        data['identifier']=profile.phone
        form = LoginAuthenticationNoCaptchaForm(request, data=data)
        if form.is_valid():
            if id_number != profile.id_number:
                return Response({'message':"身份证错误"}, status=400)
        # 同卡之后要对银行卡号进行验证
            card = Card.objects.filter(user=self.request.user, is_the_one_card=True)
            if not card.exists():
                return Response({'message':"用户需要绑定的银行卡号"}, status=400)
            card_no = request.DATA.get('card_no', "").strip()
            if not card_no:
                return Response({'message': "用户需要提供绑定的银行卡号"}, status=400)
            card = card.first()
            if card.no != card_no:
                return Response({'message': "银行卡号输入错误"}, status=400)
            return Response({'ret_code': 0})
        message = ""
        for key, value in form.errors.iteritems():
            for msg in value:
                if msg == u"用户名或者密码不正确":
                    msg = u"密码不正确"
                message+=msg
        return Response({"message":message}, status=400)


class ModifyPhoneValidateCode(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, phone):
        phone_number = phone.strip()
        new_phone_user = User.objects.filter(wanglibaouserprofile__phone=phone_number)
        if new_phone_user.exists():
            return Response({'message':"要修改的手机号已经注册网利宝，请更换其他手机号"}, status=400)
        if not AntiForAllClient(request).anti_special_channel():
            res, message = False, u"请输入验证码"
        else:
            res, message = verify_captcha(request.POST)

        if not res:
            return Response({'message': message, "type":"captcha"}, status=403)

        status, message = send_validation_code(phone_number, ip=get_client_ip(request))
        return Response({'message': message, "type":"validation"}, status=status)


class ManualModifyPhoneTemplate(TemplateView):
    template_name = 'phone_modify_manual.jade'

    def get_context_data(self, **kwargs):
        user = self.request.user
        profile = user.wanglibaouserprofile
        form = ManualModifyPhoneForm()
        modify_phone_record = ManualModifyPhoneRecord.objects.filter(user=user).first()
        if modify_phone_record and modify_phone_record.status not in [u"复审驳回", u"初审驳回"]:
            modify_phone_record = None

        return {
                'user_name':profile.name,
                'modify_phone_record':modify_phone_record
                }


class ManualModifyPhoneAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        profile = user.wanglibaouserprofile
        if not profile.id_is_valid or not profile.id_number:
            return Response({'message':"还没有实名认证"}, status=400)
        card = Card.objects.filter(user=self.request.user, is_the_one_card=True)
        if not card.exists():
            return Response({'message':"用户需要绑定的银行卡号"}, status=400)
        form = ManualModifyPhoneForm(self.request.DATA, self.request.FILES)
        if form.is_valid():
            id_front_image = form.cleaned_data.get('id_front_image')
            id_back_image = form.cleaned_data.get('id_back_image')
            id_user_image = form.cleaned_data.get('id_user_image')
            card_user_image = form.cleaned_data.get('card_user_image')
            new_phone = form.cleaned_data['new_phone']
            modify_phone_record = ManualModifyPhoneRecord.objects.filter(user=user).first()
            if modify_phone_record  and modify_phone_record.status in [u"待初审", u"初审待定", u"待复审"]:
                return Response({'message': u"您之前申请的人工修改手机号的请求还未处理完毕,请联系网利宝客服"}, status=400)
            if modify_phone_record and modify_phone_record.status in [u"复审驳回", u"初审驳回"]:
                modify_phone_record_id = int(self.request.DATA.get('modify_phone_record_id', 0))
                if modify_phone_record_id != modify_phone_record.id:
                    return Response({'message': u"申请的人工修改手机号id参数错误"}, status=400)
                manual_record = modify_phone_record
            else:
                manual_record = ManualModifyPhoneRecord()
            #todo
            manual_record.user = user
            manual_record.phone = profile.phone
            manual_record.new_phone = new_phone
            manual_record.status = u'待初审'
            manual_record.save()
            if id_front_image:
                id_front_image.name = "%s_%s_%s"%(user.id, manual_record.id, 0)
                manual_record.id_front_image = id_front_image
            if id_back_image:
                id_back_image.name = "%s_%s_%s"%(user.id, manual_record.id, 1)
                manual_record.id_back_image = id_back_image
            if id_user_image:
                id_user_image.name = "%s_%s_%s"%(user.id, manual_record.id, 2)
                manual_record.id_user_image = id_user_image
            if card_user_image:
                card_user_image.name = "%s_%s_%s"%(user.id, manual_record.id, 3)
                manual_record.card_user_image = card_user_image
            manual_record.save()
            msg = "尊敬的%s，您已申请人工审核修改手机号，申请结果将在3个工作日内通过短信发送到本手机，请留意，退订回TD【网利科技】"%profile.name
            send_messages.apply_async(kwargs={
                "phones": [new_phone, ],
                "messages": [msg, ],
            })
            return Response({'ret_code': 0})
        else:
            message = form.errors
            for key, value in form.errors.iteritems():
                message = ",".join(value)
            return Response({"message":message}, status=400)


class CancelManualModifyPhoneAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        profile = user.wanglibaouserprofile
        if not profile.id_is_valid or not profile.id_number:
            return Response({'message':"还没有实名认证"}, status=400)
        card = Card.objects.filter(user=self.request.user, is_the_one_card=True)
        if not card.exists():
            return Response({'message':"用户需要绑定的银行卡号"}, status=400)
        modify_phone_record = ManualModifyPhoneRecord.objects.filter(user=user).first()
        if not modify_phone_record or modify_phone_record.status not in [u"复审驳回", u"初审驳回"]:
            return Response({'message':"没有可以取消的申请"}, status=400)
        modify_phone_record.status = u"取消申请"
        modify_phone_record.save()
        return Response({"message": "ok"})


class SMSModifyPhoneValidateTemplate(TemplateView):

    def get_context_data(self, **kwargs):
        user = self.request.user
        profile = user.wanglibaouserprofile
        card = Card.objects.filter(user=self.request.user, is_the_one_card=True)
        is_bind_card = card.exists()
        return {
            "phone": profile.phone,
            'is_bind_card': is_bind_card,
            }


class SMSModifyPhoneValidateAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        profile = user.wanglibaouserprofile
        validate_code = request.DATA.get('validate_code', "").strip()
        id_number = request.DATA.get('id_number', "").strip()
        new_phone = request.DATA.get('new_phone', "").strip()

        if not profile.id_is_valid or not profile.id_number:
            return Response({'message':"还没有实名认证"}, status=400)
        if not validate_code or not id_number or not new_phone:
            return Response({'message':"参数为空"}, status=400)
        # 同卡之后要对银行卡号进行验证
        card = Card.objects.filter(user=self.request.user, is_the_one_card=True)
        if not card.exists():
            return Response({'message':"用户需要绑定的银行卡号"}, status=400)
        card_no = request.DATA.get('card_no', "").strip()
        if not card_no:
            return Response({'message': "用户需要提供绑定的银行卡号"}, status=400)
        card = card.first()
        if card.no != card_no:
            return Response({'message': "银行卡号输入错误"}, status=400)
        params = request.DATA
        data = {}
        for k,v in params.iteritems():
            data[k]=v
        data['identifier']=profile.phone
        form = LoginAuthenticationNoCaptchaForm(request, data=data)
        if form.is_valid():
            if form.get_user()!=user:
                return Response({'message':"用户错误"}, status=400)
            status, message = validate_validation_code(profile.phone, validate_code)
            if status != 200:
                return Response({'message':message}, status=400)
            if id_number != profile.id_number:
                return Response({'message':"身份证错误"}, status=400)
            new_phone_user = User.objects.filter(wanglibaouserprofile__phone=new_phone).first()
            if new_phone_user:
                return Response({'message':"要修改的手机号已经注册网利宝，请更换其他手机号"}, status=400)
            modify_phone_record = ManualModifyPhoneRecord.objects.filter(user=user).first()
            if modify_phone_record and modify_phone_record.status in [u"待初审", u"初审待定", u"待复审", u"复审驳回", u"初审驳回"]:
                return Response({'message':"你有还未处理结束的人工修改手机号申请，请耐心等待客服处理"}, status=400)

            sms_modify_record = SMSModifyPhoneRecord.objects.filter(user=user, phone=profile.phone, status=u'短信修改手机号提交').first()
            if not sms_modify_record:
                sms_modify_record = SMSModifyPhoneRecord()
                sms_modify_record.user = user
                sms_modify_record.phone = profile.phone
                sms_modify_record.status = u'短信修改手机号提交'
                sms_modify_record.new_phone = new_phone
                sms_modify_record.save()
            if sms_modify_record.new_phone != new_phone:
                sms_modify_record.new_phone = new_phone
                sms_modify_record.save()
            return Response({"message":'ok'})
        message = ""
        for key, value in form.errors.iteritems():
            for msg in value:
                if msg == u"用户名或者密码不正确":
                    msg = u"密码不正确"
                message+=msg
        return Response({"message":message}, status=400)


class SMSModifyPhoneTemplate(TemplateView):

    def get_context_data(self, **kwargs):
        user = self.request.user
        profile = user.wanglibaouserprofile
        new_phone = ""
        sms_modify_record = SMSModifyPhoneRecord.objects.filter(user=user, phone=profile.phone, status=u'短信修改手机号提交').first()
        if sms_modify_record:
            new_phone = sms_modify_record.new_phone

        return {
            "new_phone": new_phone,
            }


class SMSModifyPhoneAPI(APIView):
    permission_classes = (IsAuthenticated, )
    def post(self, request):
        user = request.user
        new_phone = request.DATA.get('new_phone', "").strip()
        sms_modify_record = SMSModifyPhoneRecord.objects.filter(user=user, new_phone=new_phone, status=u'短信修改手机号提交').first()
        if not sms_modify_record:
            return Response({'message':u"还没有短信申请修改手机号"}, status=400)
        profile = user.wanglibaouserprofile
        validate_code = request.DATA.get('validate_code', "").strip()
        if not validate_code:
            return Response({'message':"验证码不能为空"}, status=400)
        status, message = validate_validation_code(new_phone, validate_code)
        if status != 200:
            return Response({'message':message}, status=400)
        new_phone_user = User.objects.filter(wanglibaouserprofile__phone=new_phone).first()
        if new_phone_user:
            return Response({'message':"要修改的手机号已经注册网利宝，请更换其他手机号"}, status=400)
        card = Card.objects.filter(user=self.request.user, is_the_one_card=True)
        if not card.exists():
            return Response({'message':"用户需要绑定的银行卡号"}, status=400)
        with transaction.atomic(savepoint=True):
            old_phone = profile.phone
            profile.phone = new_phone
            profile.save()
            PhoneValidateCode.objects.filter(phone=old_phone).delete()
            sms_modify_record.status=u'短信修改手机号成功'
            sms_modify_record.save()
            #todo force user login again
            msg = "尊敬的%s，您已成功修改绑定新手机号，请使用新的手机号进行登陆，密码与原登录密码相同。感谢您的支持。退订回TD【网利科技】"%profile.name
            send_messages.apply_async(kwargs={
                "phones": [new_phone, ],
                "messages": [msg, ],
            })
            return Response({'message':'ok'})


class LoginCounterVerifyAPI(DecryptParmsAPIView):
    """
    登录次数验证,下面4个情况当天错误次数清零处理
    1、重置登录密码
    2、登录成功后
    3、注销登录
    4、6次机会内验证正确
    5、第二天清零
    """

    permission_classes = (IsAuthenticated, )

    def post(self, request):

        # from django.db.models import F
        from wanglibao_profile.models import WanglibaoUserProfile

        now = timezone.now()
        today_start = local_to_utc(now, 'min')
        today_end = local_to_utc(now, 'max')
        user = request.user
        password = self.params.get('password').strip()

        # 密码错误，请重新输入
        # 错误大于6次, 密码错误频繁，为账户安全建议重置
        user_profile = WanglibaoUserProfile.objects.get(user=user)
        failed_count = user_profile.login_failed_count

        if failed_count >= 6 and today_start < now <= today_end:
            msg = {'ret_code': 80002, 'message': u'密码错误频繁，为账户安全建议重置'}
        else:
            if user.check_password(password):
                user_profile.login_failed_count = 0
                user_profile.login_failed_time = now
                user_profile.save()
                return Response({'ret_code': 0, 'message': 'ok'})
            else:
                msg = {'ret_code': 80001, 'message': u'密码错误，请重新输入'}

                if today_start < now <= today_end:
                    user_profile.login_failed_count = failed_count + 1
                    user_profile.login_failed_time = now
                else:
                    user_profile.login_failed_count = 1
                    user_profile.login_failed_time = now

                user_profile.save()

        return Response(msg)


class MarginRecordsAPIView(APIView):
    """
    用户资金账户记录
    """
    permission_classes = (IsAuthenticated, )

    @staticmethod
    def post(request):
        from wanglibao_margin.margin_record import margin_records
        res = margin_records(request)
        return Response(res)

