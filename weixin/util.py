# encoding:utf-8
from wanglibao_p2p.models import P2PEquity
from wanglibao_buy.models import FundHoldInfo
from django.template import Template, Context
from django.template.loader import get_template
from .models import WeixinAccounts, WeixinUser, WeiXinUserActionRecord, SceneRecord, UserDailyActionRecord
from wechatpy import WeChatClient
from wechatpy.exceptions import WeChatException
from misc.models import Misc
from experience_gold.backends import SendExperienceGold
from django.conf import settings

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime
from django.db import transaction
import logging
import time
import json
import urllib
import re


logger = logging.getLogger("weixin")

BASE_WEIXIN_URL = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_base&state={state}#wechat_redirect"
FWH_LOGIN_URL = ""
FWH_REGISTER_URL = ""
FWH_UNBIND_URL = ""

def get_fwh_login_url(next=None):
    m = Misc.objects.filter(key='weixin_qrcode_info').first()
    if m and m.value:
        info = json.loads(m.value)
        if isinstance(info, dict) and info.get("fwh"):
            original_id = info.get("fwh")
            account = WeixinAccounts.getByOriginalId(original_id)
            fwh_login_url = settings.CALLBACK_HOST + "/weixin/sub_login/"
            if next:
                fwh_login_url += "?next=%s"%urllib.quote(next)
                return BASE_WEIXIN_URL.format(appid=account.app_id, redirect_uri=fwh_login_url, state=original_id)
            fwh_unbind_url = settings.CALLBACK_HOST + "/weixin/unbind/"
            global FWH_LOGIN_URL
            FWH_LOGIN_URL = BASE_WEIXIN_URL.format(appid=account.app_id, redirect_uri=fwh_login_url, state=original_id)
            global FWH_UNBIND_URL
            FWH_UNBIND_URL = BASE_WEIXIN_URL.format(appid=account.app_id, redirect_uri=fwh_unbind_url, state=original_id)
            return FWH_LOGIN_URL


if not FWH_LOGIN_URL:
   get_fwh_login_url()


def redirectToJumpPage(message, next=None):
    url = reverse('jump_page')+'?message=%s'% message
    if next:
        return HttpResponseRedirect(next)
        # url = reverse('jump_page')+'?message=%s&next=%s'% (message, next)
    return HttpResponseRedirect(url)

def sendTemplate(weixin_user, message_template):
    weixin_account = WeixinAccounts.getByOriginalId(weixin_user.account_original_id)
    # account = Account.objects.get(original_id=weixin_user.account_original_id)
    client = WeChatClient(weixin_account.app_id, weixin_account.app_secret)
    client.message.send_template(weixin_user.openid, template_id=message_template.template_id,
                                 top_color=message_template.top_color, data=message_template.data,
                                 url=message_template.url)


def getOrCreateWeixinUser(openid, weixin_account):
    old_subscribe = 0
    w_user = WeixinUser.objects.filter(openid=openid).first()
    if w_user and w_user.subscribe:
        old_subscribe = 1
    if not w_user:
        w_user = WeixinUser()
        w_user.openid = openid
        w_user.account_original_id = weixin_account.db_account.original_id
        w_user.save()
    if w_user.account_original_id != weixin_account.db_account.original_id:
        w_user.account_original_id = weixin_account.db_account.original_id
        w_user.save()
    if not w_user.nickname or not w_user.subscribe or not w_user.subscribe_time:
        try:
            user_info = weixin_account.db_account.get_user_info(openid)
            w_user.nickname = user_info.get('nickname', "")
            w_user.sex = user_info.get('sex', 0)
            w_user.city = user_info.get('city', "")
            w_user.country = user_info.get('country', "")
            w_user.headimgurl = user_info.get('headimgurl', "")
            w_user.unionid =  user_info.get('unionid', '')
            w_user.province = user_info.get('province', '')
            w_user.subscribe = user_info.get('subscribe', 0)
            # if not w_user.subscribe_time:
            w_user.subscribe_time = user_info.get('subscribe_time', 0)
            w_user.nickname = filter_emoji( w_user.nickname, "*")
            w_user.save()
        except WeChatException, e:
            logger.debug(e.message)
            pass

    return w_user, old_subscribe

def filter_emoji(desstr,restr=''):
    '''
    过滤表情
    '''
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(restr, desstr)


def _process_record(w_user, user, type, describe):
    war = WeiXinUserActionRecord()
    war.w_user_id = w_user.id
    war.user_id = user.id
    war.action_type = type
    war.action_describe = describe
    war.create_time = int(time.time())
    war.save()


def _process_scene_record(w_user, scene_str):
    sr = SceneRecord()
    sr.openid = w_user.openid
    sr.scene_str=scene_str
    sr.create_time = int(time.time())
    sr.save()

def bindUser(w_user, user):
    is_first_bind = False
    if w_user.user:
        if w_user.user.id==user.id:
            return 1, u'你已经绑定, 请勿重复绑定'
        return 2, u'你微信已经绑定%s'%w_user.user.wanglibaouserprofile.phone
    other_w_user = WeixinUser.objects.filter(user=user, account_original_id=w_user.account_original_id).first()
    if other_w_user:
        msg = u"你的手机号[%s]已经绑定微信[%s]"%(user.wanglibaouserprofile.phone, other_w_user.nickname)
        return 3, msg
    w_user.user = user
    w_user.bind_time = int(time.time())
    w_user.save()
    _process_record(w_user, user, 'bind', "绑定网利宝")

    if not user.wanglibaouserprofile.first_bind_time:
        user.wanglibaouserprofile.first_bind_time = w_user.bind_time
        user.wanglibaouserprofile.save()
        is_first_bind = True
    from tasks import bind_ok
    bind_ok.apply_async(kwargs={
        "openid": w_user.openid,
        "is_first_bind":is_first_bind,
    },
                        queue='celery01'
                        )
    return 0, u'绑定成功'

def unbindUser(w_user, user):
    w_user.user = None
    w_user.unbind_time=int(time.time())
    w_user.save()
    _process_record(w_user, user, 'unbind', "解除绑定")

def getAccountInfo(user):

    p2p_equities = P2PEquity.objects.filter(user=user).filter(product__status__in=[
        u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
    ]).select_related('product')
    unpayed_principle = 0
    p2p_total_paid_interest = 0
    p2p_total_unpaid_interest = 0
    p2p_activity_interest = 0
    p2p_total_paid_coupon_interest = 0
    p2p_total_unpaid_coupon_interest = 0
    equity_total = 0
    for equity in p2p_equities:
        equity_total += equity.equity
        if equity.confirm:
            unpayed_principle += equity.unpaid_principal  # 待收本金
            p2p_total_paid_interest += equity.pre_paid_interest  # 累积收益
            p2p_total_unpaid_interest += equity.unpaid_interest  # 待收益
            p2p_total_paid_coupon_interest += equity.pre_paid_coupon_interest  # 加息券已收总收益
            p2p_total_unpaid_coupon_interest += equity.unpaid_coupon_interest  # 加息券待收总收益
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
    res = {
        'total_asset': float(p2p_total_asset + fund_total_asset),  # 总资产
        'p2p_margin': float(p2p_margin),  # P2P余额
        'p2p_total_unpaid_interest': float(p2p_total_unpaid_interest + p2p_total_unpaid_coupon_interest),  # p2p总待收益
        'p2p_total_paid_interest': float(p2p_total_paid_interest + p2p_activity_interest + p2p_total_paid_coupon_interest),  # P2P总累积收益
        'equity_total':equity_total #投资金额
    }
    return res


def _generate_ajax_template(content, template_name=None):

    context = Context({
        'results': content,
    })

    if template_name:
        template = get_template(template_name)
    else:
        template = Template('<div></div>')

    return template.render(context)


def process_user_daily_action(user, action_type=u'sign_in'):

    if action_type not in [u'share', u'sign_in']:
        return -1, False, None
    today = datetime.date.today()
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
    daily_record = UserDailyActionRecord.objects.filter(user=user, create_date=today, action_type=action_type).first()
    if not daily_record:
        UserDailyActionRecord.objects.create(
            user=user,
            action_type=action_type
        )
    if record.status:
        return 1, False, daily_record
    with transaction.atomic():
        daily_record = UserDailyActionRecord.objects.select_for_update().filter(user=user, create_date=today, action_type=action_type).first()
        seg = SendExperienceGold(user)
        experience_event = getSignExperience_gold()
        if experience_event:
            experience_record_id, experience_event = seg.send(experience_event.id)
            daily_record.experience_record_id = experience_record_id
        daily_record.status=True
        yesterday_record = UserDailyActionRecord.objects.filter(user=user, create_date=yesterday, action_type=action_type).first()
        continue_days = 1
        if yesterday_record:
            continue_days += yesterday_record.continue_days
        daily_record.continue_days=continue_days
        daily_record.save()
    return 0, True, daily_record


def getSignExperience_gold():
    now = timezone.now()
    query_object = ExperienceEvent.objects.filter(invalid=False, give_mode='weixin_sign_in',
                                                      available_at__lt=now, unavailable_at__gt=now)
    experience_events = query_object.order_by('amount').all()
    length = len(experience_events)
    if length > 1:
        random_int = random.randint(0, length-1)
        return experience_events[random_int]
    return None