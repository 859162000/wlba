# encoding:utf-8
from django.views.generic import TemplateView
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from django.template import Template, Context
from django.contrib.auth import login as auth_login, logout
from django.core.urlresolvers import reverse
import logging
import base64,urllib
import datetime, time
import traceback
from wanglibao_account.backends import invite_earning
from weixin.models import UserDailyActionRecord, SeriesActionActivity, SeriesActionActivityRule, WeixinUser, WeiXinUserActionRecord
from experience_gold.models import ExperienceEventRecord
from util import process_user_daily_action
from wanglibao_reward.models import ActivityRewardRecord
from wanglibao_redpack.models import RedPackEvent
from wanglibao_redpack.backends import give_activity_redpack_for_hby, get_start_end_time
from wanglibao_redpack.backends import _send_message_for_hby
from experience_gold.backends import SendExperienceGold
from wanglibao_rest.utils import split_ua
from marketing.models import Reward
from marketing.utils import local_to_utc
from wanglibao_activity.backends import _keep_reward_record, _send_message_template
from wanglibao_activity.models import Activity
from tasks import sentCustomerMsg
from wanglibao_invite.utils import getWechatDailyReward
from wanglibao_invite.models import WechatUserDailyReward
from weixin.models import WeixinAccounts
from weixin.util import redirectToJumpPage, getOrCreateWeixinUser, get_weixin_code_url, getMiscValue
from wechatpy.oauth import WeChatOAuth
from wechatpy.exceptions import WeChatException
from experience_gold.models import ExperienceEvent
from .forms import OpenidAuthenticationForm
from wanglibao_invite.models import InviteRelation, UserExtraInfo
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_invite.invite_common import ShareInviteRegister
from wanglibao_account import message as inside_message
from wanglibao_p2p.models import P2PRecord

logger = logging.getLogger("weixin")
# https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx18689c393281241e&redirect_uri=http://2ea0ef54.ngrok.io/weixin/award_index/&response_type=code&scope=snsapi_base&state=1#wechat_redirect

class InviteWeixinFriendTemplate(TemplateView):
    template_name = "sub_invite_server.jade"

    def get_context_data(self, **kwargs):
        user = self.request.user
        earning = 0
        if user:
            earning = invite_earning(user)

        return {
            "earning":earning,
            "callback_host":settings.CALLBACK_HOST,
            "url": base64.b64encode(user.wanglibaouserprofile.phone),
        }
    def dispatch(self, request, *args, **kwargs):
        self.url_name = 'sub_invite'
        return super(InviteWeixinFriendTemplate, self).dispatch(request, *args, **kwargs)

class DailyActionAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        action_type = unicode(request.POST.get('action_type', '').strip())
        if not action_type or action_type not in [u'share', u'sign_in']:
            return Response({'ret_code':-1, 'message':'系统错误'})
        user_agent = request.META['HTTP_USER_AGENT']
        platform = u"app"
        if "MicroMessenger" in user_agent:
            platform = u"weixin"

        ret_code, status, daily_record = process_user_daily_action(user, platform=platform, action_type=action_type)
        if ret_code == 2:
            return Response({'ret_code': -1, 'message':'系统忙，请重试'})
        data = {'status': status, 'continue_days': daily_record.continue_days}
        if status and daily_record.experience_record_id:
            experience_record = ExperienceEventRecord.objects.get(id=daily_record.experience_record_id)
            experience_amount=experience_record.event.amount
            data['experience_amount'] = experience_amount

        return Response({'ret_code': 0, "data":data})

class GetContinueActionReward(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        user = request.user
        days = request.POST.get('days', '').strip()
        # days = request.GET.get('days', '').strip()
        if not days or not days.isdigit():
            return Response({'ret_code':-1, 'message':u'参数错误'})
        days = int(days)

        today = datetime.date.today()
        # yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
        sign_record = UserDailyActionRecord.objects.filter(user=user, create_date=today, action_type=u'sign_in').first()
        if not sign_record or not sign_record.status:
            return Response({'ret_code':-1, 'message':u'不符合领取条件'})
        activities = SeriesActionActivity.objects.filter(action_type=u'sign_in', is_stopped=False, start_at__lte=timezone.now(), end_at__gte=timezone.now()).all()
        current_activity= None

        for activity in activities:
            if activity.days==days:
                current_activity=activity
        if not current_activity:
            return Response({'ret_code':-1, 'message':u'不符合领取条件'})

        length = len(activities)
        maxDayNote=activities[length-1].days
        if sign_record.continue_days < maxDayNote:
            recycle_continue_days = sign_record.continue_days
        elif sign_record.continue_days % maxDayNote == 0:
            recycle_continue_days = maxDayNote
        else:
            recycle_continue_days = sign_record.continue_days % maxDayNote
        # recycle_continue_days = sign_record.continue_days % (maxDayNote + 1)
        if recycle_continue_days!=days:
            return Response({'ret_code':-1, 'message':u'不符合领取条件'})

        reward_record, create = ActivityRewardRecord.objects.get_or_create(
                    activity_code=current_activity.code,
                    create_date=today,
                    user=user
                    )
        if reward_record.status:
           return Response({'ret_code':-1, 'message':u'奖励已经领取过了'})
        device = split_ua(self.request)
        user_agent = request.META['HTTP_USER_AGENT']
        is_weixin = False
        if "MicroMessenger" in user_agent:
            is_weixin = True
        device_type = device['device_type']
        events = []
        records = []
        experience_events = []
        rewards = []
        redpack_txts = []
        redpack_record_ids = ""
        experience_record_ids = ""
        with transaction.atomic():
            reward_record = ActivityRewardRecord.objects.select_for_update().filter(activity_code=current_activity.code, create_date=today, user=user).first()
            if reward_record.status:
                return Response({'ret_code':-1, 'message':u'奖励已经领取过了'})
            rules = SeriesActionActivityRule.objects.filter(activity=current_activity, is_used=True)
            for rule in rules:
                sub_redpack_record_ids, sub_experience_record_ids = self.giveReward(user, rule, events, experience_events, records, redpack_txts, device_type)
                if isinstance(sub_redpack_record_ids, Response):
                    return sub_redpack_record_ids
                if isinstance(sub_experience_record_ids, Response):
                    return sub_experience_record_ids

                redpack_record_ids += sub_redpack_record_ids
                experience_record_ids += sub_experience_record_ids
                if rule.gift_type == "reward":
                    reward = None
                    reward_list = rule.reward.split(",")
                    for reward_type in reward_list:
                        now = timezone.now()
                        reward = Reward.objects.filter(type=reward_type,
                                                       is_used=False,
                                                       end_time__gte=now).first()
                        if reward:
                            break
                    if reward:
                        reward.is_used = True
                        reward.save()
                        # 记录奖品发放流水
                        description = '=>'.join([rule.rule_name, reward.type])
                        has_reward_record = _keep_reward_record(user, reward, description)
                        reward_content = reward.content
                        end_date = timezone.localtime(reward.end_time).strftime("%Y年%m月%d日")
                        name = reward.type
                        context = Context({
                            # 'mobile': safe_phone_str(user.wanglibaouserprofile.phone),
                            'reward': reward_content,
                            'end_date': end_date,
                            'name': name,
                        })
                        if has_reward_record:
                            rewards.append(reward)
                            redpack_txts.append(name)
                            if rule.msg_template:
                                msg = Template(rule.msg_template)
                                content = msg.render(context)
                                _send_message_template(user, rule.rule_name, content)
                    else:
                        sub_redpack_record_ids, sub_experience_record_ids = self.giveReward(user, rule, events, experience_events, records,redpack_txts, device_type, is_addition=True)
                        if isinstance(sub_redpack_record_ids, Response):
                            return sub_redpack_record_ids
                        if isinstance(sub_experience_record_ids, Response):
                            return sub_experience_record_ids
                        redpack_record_ids += sub_redpack_record_ids
                        experience_record_ids += sub_experience_record_ids

            reward_record.redpack_record_ids = redpack_record_ids
            reward_record.experience_record_ids = experience_record_ids
            reward_record.activity_code_time = timezone.now()
            reward_record.status = True
            reward_record.activity_desc=u'用户领取连续%s天签到奖励'%days
            reward_record.save()
        try:
            w_user = WeixinUser.objects.filter(user=user).first()
            for idx, event in enumerate(events):
                record = records[idx]
                start_time, end_time = get_start_end_time(event.auto_extension, event.auto_extension_days,
                                                          record.created_at, event.available_at, event.unavailable_at)
                _send_message_for_hby(request.user, event, end_time)
                if is_weixin and w_user:
                    sentCustomerMsg.apply_async(kwargs={
                            "txt":"恭喜您获得连续%s天签到奖励\n签到奖励：%s\n有效期至：%s\n快去我的账户－理财券页面查看吧！"%(days, getattr(event, "desc_text", "优惠券"), end_time.strftime('%Y年%m月%d日')), #\n兑换码:%s
                            "openid":w_user.openid,
                        },
                                                    queue='celery02')
            if is_weixin and w_user:
                for reward in rewards:
                    sentCustomerMsg.apply_async(kwargs={
                            "txt":"恭喜您获得连续%s天签到奖励\n签到奖励：%s\n有效期至：%s\n兑换码：%s\n天天签到不要停，快去兑换吧！"%(days, reward.type, timezone.localtime(reward.end_time).strftime("%Y年%m月%d日"), reward.content), #\n兑换码:%s
                            "openid":w_user.openid,
                        },
                                                    queue='celery02')
            if is_weixin and w_user:
                for experience_event in experience_events:
                    sentCustomerMsg.apply_async(kwargs={
                            "txt":"恭喜您获得连续%s天签到奖励\n签到奖励：%s\n快去我的账户－体验金页面查看吧！"%(days, getattr(experience_event, "desc_text", "体验金")),
                            "openid":w_user.openid,
                        },
                                                    queue='celery02')

        except Exception, e:
            logger.debug(traceback.format_exc())
        logger.debug(redpack_txts)
        result_msg = "恭喜您~领取%s成功!"%(",".join(redpack_txts))
        mysterious_day = maxDayNote - recycle_continue_days
        if maxDayNote == recycle_continue_days:
            mysterious_day = maxDayNote
        return Response({"ret_code":0, "message":result_msg, "mysterious_day":mysterious_day})

    def giveReward(self, user, rule, events, experience_events, records, redpack_txts, device_type, is_addition=False):
        redpack_ids = None
        experience_record_ids = ""
        redpack_record_ids = ""
        if not is_addition:
            if rule.gift_type == "redpack":
                redpack_ids = rule.redpack.split(',')

            if rule.gift_type == "experience_gold":
                experience_record_ids = self.give_experience(user, experience_events, redpack_txts, rule.redpack)
                if isinstance(experience_record_ids, Response):
                    return None, experience_record_ids
        else:
            if rule.addition_gift_type == "redpack":
                redpack_ids = rule.addition_redpack.split(',')

            if rule.addition_gift_type == "experience_gold":
                experience_record_ids = self.give_experience(user, experience_events, redpack_txts, rule.addition_redpack)
                if isinstance(experience_record_ids, Response):
                    return None, experience_record_ids
        if redpack_ids:
            redpack_record_ids = self.give_redpack(user, events, records, redpack_txts, redpack_ids, device_type)
            if isinstance(redpack_record_ids, Response):
                return redpack_record_ids, None
        return redpack_record_ids, experience_record_ids

    def give_redpack(self, user, events, records, redpack_txts, redpack_ids, device_type):
        redpack_record_ids = ""
        # redpack_ids = rule.redpack.split(',')
        for redpack_id in redpack_ids:
            redpack_event = RedPackEvent.objects.filter(id=redpack_id).first()
            if not redpack_event:
                return Response({"ret_code":-1,"message":'系统错误'})
            status, messege, record = give_activity_redpack_for_hby(user, redpack_event, device_type)
            if not status:
                return Response({"ret_code":-1,"message":messege})
            redpack_text = "None"
            if redpack_event.rtype == 'interest_coupon':
                redpack_text = "%s%%加息券"%redpack_event.amount
            if redpack_event.rtype == 'percent':
                redpack_text = "%s%%百分比红包"%redpack_event.amount
            if redpack_event.rtype == 'direct':
                redpack_text = "%s元直抵红包"%int(redpack_event.amount)
            setattr(redpack_event, 'desc_text', redpack_text)
            redpack_txts.append(redpack_text)
            redpack_record_ids += (str(record.id) + ",")
            events.append(redpack_event)
            records.append(record)
        return redpack_record_ids

    def give_experience(self, user, experience_events, redpack_txts, experience_event_id):
        experience_record_ids = ""
        experience_record_id, experience_event = SendExperienceGold(user).send(pk=experience_event_id)
        if not experience_record_id:
            return Response({"ret_code":-1, "message":'体验金发放失败'})
        experience_events.append(experience_event)
        experience_event_text = '%s元体验金'%int(experience_event.amount)
        redpack_txts.append(experience_event_text)
        setattr(experience_event, 'desc_text', experience_event_text)
        experience_event.experience_event_text = experience_event_text
        experience_record_ids += (str(experience_record_id) + ",")
        return experience_record_ids

class GetSignShareInfo(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        today = datetime.date.today()
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
        sign_record = UserDailyActionRecord.objects.filter(user=user, create_date=today, action_type=u'sign_in').first()
        share_record = UserDailyActionRecord.objects.filter(user=user, create_date=today, action_type=u'share').first()
        data = {}
        sign_info = data.setdefault('sign_in', {})
        # sign_total_count = UserDailyActionRecord.objects.filter(user=user, action_type=u'sign_in').count()
        # sign_info['sign_total_count'] = sign_total_count
        sign_info['status'] = False
        sign_info['amount']=0
        sign_info['today_should_continue_days'] = 0
        if sign_record and sign_record.status:
            sign_info['status'] = True
            sign_info['continue_days'] = sign_record.continue_days
            sign_info['today_should_continue_days'] = sign_record.continue_days
            if sign_record.experience_record_id:
                experience_record = ExperienceEventRecord.objects.get(id=sign_record.experience_record_id)
                sign_info['amount']=experience_record.event.amount
        else:
            yesterday_sign_record = UserDailyActionRecord.objects.filter(user=user, create_date=yesterday, action_type=u'sign_in').first()
            sign_info['continue_days'] = 0
            sign_info['today_should_continue_days'] = 0
            if yesterday_sign_record:
                sign_info['continue_days'] = yesterday_sign_record.continue_days
                sign_info['today_should_continue_days'] = yesterday_sign_record.continue_days + 1
        nextDayNote = None
        activities = SeriesActionActivity.objects.filter(is_stopped=False, start_at__lte=timezone.now(), end_at__gte=timezone.now()).all()
        length = len(activities)
        if length > 0:
            start_day = 1
            maxDayNote=activities[length-1].days
            if sign_info['continue_days'] < maxDayNote:
                recycle_continue_days = sign_info['continue_days']
            elif sign_info['continue_days'] % maxDayNote == 0:
                recycle_continue_days = maxDayNote
            else:
                recycle_continue_days = sign_info['continue_days'] % maxDayNote
            today_should_recycle_continue_days = recycle_continue_days
            if sign_info['today_should_continue_days'] != sign_info['continue_days']:
                if sign_info['today_should_continue_days'] < maxDayNote:
                    today_should_recycle_continue_days = sign_info['today_should_continue_days']
                elif sign_info['today_should_continue_days'] % maxDayNote == 0:
                    today_should_recycle_continue_days = maxDayNote
                else:
                    today_should_recycle_continue_days = sign_info['today_should_continue_days'] % maxDayNote
            if maxDayNote==recycle_continue_days and recycle_continue_days != today_should_recycle_continue_days:
                sign_info['mysterious_day'] = maxDayNote
                sign_info['current_day'] = 0
            else:
                sign_info['mysterious_day'] = maxDayNote-recycle_continue_days
                sign_info['current_day'] = recycle_continue_days

            for activity in activities:
                if activity.days >= today_should_recycle_continue_days:
                    nextDayNote=activity.days
                    sign_info['continueGiftFetched']=False
                    if activity.days == today_should_recycle_continue_days:
                        reward_record = ActivityRewardRecord.objects.filter(activity_code=activity.code, create_date=today, user=user).first()
                        if reward_record and reward_record.status:
                            sign_info['continueGiftFetched']=reward_record.status#是否已经领取神秘礼物
                            if maxDayNote == activity.days:
                                sign_info['mysterious_day'] = maxDayNote
                    break
                start_day = activity.days + 1
            sign_info['isMysteriGift'] = maxDayNote==today_should_recycle_continue_days

            sign_info['nextDayNote'] = nextDayNote#下一个神秘礼物在第几天
            sign_info['start_day'] = start_day

        share_info = data.setdefault('share', {})
        share_info['status'] = False
        share_info['amount']=0
        if share_record and share_record.status:
            share_info['status'] = True
            if share_record.experience_record_id:
                experience_record = ExperienceEventRecord.objects.get(id=share_record.experience_record_id)
                share_info['amount']=experience_record.event.amount
        return Response({"ret_code": 0, "data": data})

class WechatShareInviteBindTemplate(TemplateView):
    template_name = ""

    def get_context_data(self, **kwargs):
        next = self.request.GET.get('next')
        return {"next":next}

    def dispatch(self, request, *args, **kwargs):
        self.openid = self.request.session.get('openid')
        return super(WechatShareInviteBindTemplate, self).dispatch(request, *args, **kwargs)

class FetchWechatHBYReward(APIView):
    permission_classes = ()
    def post(self, request):
        openid = self.request.session.get('openid')
        if not openid:
            return Response({"ret_code": -1, "msg": "系统错误"})
        activity = Activity.objects.filter(code="hby").first()
        if not activity:
            return Response({"ret_code": -1, "message":"没有该活动"})
        if activity.is_stopped:
            return Response({"ret_code": -1, "message":"活动已经截止"})
        now = timezone.now()
        if activity.start_at > now:
            return Response({"ret_code": -1, "message":"活动还未开始"})
        if activity.end_at < now:
            return Response({"ret_code": -1, "message":"活动已经结束"})
        w_user = WeixinUser.objects.filter(openid=openid).first()
        ret_code, msg, amount = getWechatDailyReward(openid)
        is_bind = True if w_user.user else False
        return Response({"ret_code": ret_code, "msg": msg, "is_bind":is_bind, "amount":amount})

class WechatInviteTemplate(TemplateView):
    template_name = ""
    def get_context_data(self, **kwargs):
        today = datetime.datetime.today()
        # w_user = WeixinUser.objects.filter(user=self.request.user).first()
        fphone = self.request.session.get(settings.SHARE_INVITE_KEY, "")
        inviter_head_url = ""
        if fphone:
            friend_profile = WanglibaoUserProfile.objects.filter(phone=fphone).first()
            f_w_user = WeixinUser.objects.filter(user=friend_profile.user).first()
            if f_w_user:
                inviter_head_url = f_w_user.headimgurl
            fphone = base64.b64encode(fphone + '=')
        friend_num=0
        reward_text = ""
        reward_type = ""
        fetched = False
        fetched_date = ""
        is_bind = False
        invite_experience_amount = 0
        userprofile = self.request.user.wanglibaouserprofile
        share_url = settings.CALLBACK_HOST + reverse("hby_weixin_share") + "?%s=%s&%s=%s"%(settings.SHARE_INVITE_KEY, base64.b64encode(userprofile.phone+"="), settings.PROMO_TOKEN_QUERY_STRING, "hby")
        share_url = get_weixin_code_url(share_url)
        user = self.w_user.user
        if self.w_user:
            is_bind = True if user else False
            if is_bind:
                w_daily_reward = WechatUserDailyReward.objects.filter(user=user, create_date=today, status=True).first()
                if not w_daily_reward:
                    w_daily_reward = WechatUserDailyReward.objects.filter(w_user=self.w_user, create_date=today).first()
            else:
                w_daily_reward = WechatUserDailyReward.objects.filter(w_user=self.w_user, create_date=today).first()

            if w_daily_reward:# and w_daily_reward.status
                fetched = True
                if w_daily_reward.reward_type == "redpack":
                    redpack_event = RedPackEvent.objects.get(id=w_daily_reward.redpack_id)
                    if redpack_event.rtype == 'interest_coupon':
                        reward_text = "%s%%"%redpack_event.amount
                    if redpack_event.rtype == 'percent':
                        reward_text = "%s%%"%redpack_event.amount
                    if redpack_event.rtype == 'direct':
                        reward_text = "%s元"%int(redpack_event.amount)
                    reward_type = redpack_event.rtype
                if w_daily_reward.reward_type == "experience_gold":
                    experience_event = ExperienceEvent.objects.filter(pk=w_daily_reward.experience_gold_id).first()
                    reward_text = "%s元"%int(experience_event.amount)
                    reward_type = w_daily_reward.reward_type
            friend_num = InviteRelation.objects.filter(inviter=self.request.user).count()

            extro_info = UserExtraInfo.objects.filter(user=self.request.user).first()
            if extro_info:
                invite_experience_amount = extro_info.invite_experience_amount
        weixin_qrcode_info = getMiscValue("weixin_qrcode_info")
        ShareInviteRegister(self.request).clear_session()
        logger.debug('--------------------------share_url::'+share_url)
        logger.debug('-----------------------------------%s'%{
            "fetched":fetched,
            "fetched_date":fetched_date,
            "reward_text":reward_text,
            "reward_type":reward_type,
            "is_bind": is_bind,
            "friend_num":friend_num,
            "invite_experience_amount":invite_experience_amount,
            "inviter_head_url":inviter_head_url,
            "share_url":share_url,
            "fphone":fphone,
            "original_id":weixin_qrcode_info.get("fwh", ""),
            "weixin_channel_code":"hby",
        })
        return {
            "fetched":fetched,
            "fetched_date":fetched_date,
            "reward_text":reward_text,
            "reward_type":reward_type,
            "is_bind": is_bind,
            "friend_num":friend_num,
            "invite_experience_amount":invite_experience_amount,
            "inviter_head_url":inviter_head_url,
            "share_url":share_url,
            "fphone":fphone,
            "original_id":weixin_qrcode_info.get("fwh", ""),
            "weixin_channel_code":"hby",
        }

    def dispatch(self, request, *args, **kwargs):
        self.openid = self.request.session.get('openid')
        code = request.GET.get('code', "")
        state = request.GET.get('state', "")
        if not self.openid:
            error_msg = ""
            if code and state:
                try:
                    account = WeixinAccounts.getByOriginalId(state)
                    request.session['account_key'] = account.key
                    oauth = WeChatOAuth(account.app_id, account.app_secret, )
                    user_info = oauth.fetch_access_token(code)
                    self.openid = user_info.get('openid')
                    request.session['openid'] = self.openid
                    self.w_user, old_subscribe = getOrCreateWeixinUser(self.openid, account)
                except WeChatException, e:
                    error_msg = e.message
            else:
                error_msg = u"code or state is None"
            if error_msg:
                return redirectToJumpPage(error_msg)
        else:
            self.w_user = WeixinUser.objects.filter(openid=self.openid).first()
        if not self.w_user.user:
            next_uri=reverse("hby_weixin_invite")
            return redirectToJumpPage("", next=settings.CALLBACK_HOST + reverse("si_bind_login")+"?next=%s"%urllib.quote(settings.CALLBACK_HOST+next_uri))
        if request.user.is_authenticated():
            if self.w_user.user==request.user:
                return super(WechatInviteTemplate, self).dispatch(request, *args, **kwargs)
        form = OpenidAuthenticationForm(self.openid, data=request.GET)
        if form.is_valid():
            auth_login(request, form.get_user())
        return super(WechatInviteTemplate, self).dispatch(request, *args, **kwargs)


class WechatShareTemplate(TemplateView):
    template_name = ""

    def get_context_data(self, **kwargs):
        today = datetime.datetime.today()
        fetched = False
        reward_text = ""
        reward_type = ""
        fetched_date = ""
        friend_num = 0
        invite_experience_amount = 0
        fphone = self.request.session.get(settings.SHARE_INVITE_KEY, "")
        inviter_head_url = ""
        if fphone:
            friend_profile = WanglibaoUserProfile.objects.filter(phone=fphone).first()
            f_w_user = WeixinUser.objects.filter(user=friend_profile.user).first()
            if f_w_user:
                inviter_head_url = f_w_user.headimgurl
            fphone = base64.b64encode(fphone+"=")

        w_daily_reward = WechatUserDailyReward.objects.filter(w_user=self.w_user, create_date=today).first()
        if self.request.user.is_authenticated():
            friend_num = InviteRelation.objects.filter(inviter=self.request.user).count()
            extro_info = UserExtraInfo.objects.filter(user=self.request.user).first()
            if extro_info:
                invite_experience_amount = extro_info.invite_experience_amount
            if w_daily_reward and w_daily_reward.status:
                fetched = True
        else:
            if w_daily_reward:
                fetched = True
            else:
                fetched = False
                w_daily_reward = WechatUserDailyReward.objects.filter(w_user=self.w_user, status=False).first()
                if w_daily_reward:
                    fetched_date = str(w_daily_reward.create_date).split(" ")[0]

        if w_daily_reward and w_daily_reward.reward_type == "redpack":
            redpack_event = RedPackEvent.objects.get(id=w_daily_reward.redpack_id)
            if redpack_event.rtype == 'interest_coupon':
                reward_text = "%s%%"%redpack_event.amount
            if redpack_event.rtype == 'percent':
                reward_text = "%s%%"%redpack_event.amount
            if redpack_event.rtype == 'direct':
                reward_text = "%s元"%int(redpack_event.amount)
            reward_type = redpack_event.rtype
        if w_daily_reward and w_daily_reward.reward_type == "experience_gold":
            experience_event = ExperienceEvent.objects.filter(pk=w_daily_reward.experience_gold_id).first()
            reward_text = "%s元"%int(experience_event.amount)
            reward_type = w_daily_reward.reward_type
        weixin_qrcode_info = getMiscValue("weixin_qrcode_info")
        ShareInviteRegister(self.request).clear_session()
        logger.debug('-------share----------------------------%s'%{
            "fetched":fetched,
            "fetched_date":fetched_date,
            "reward_text":reward_text,
            "reward_type":reward_type,
            "is_bind": self.request.user.is_authenticated(),
            "friend_num":friend_num,
            "invite_experience_amount":invite_experience_amount,
            "inviter_head_url":inviter_head_url,
            "fphone": fphone,
            "original_id":weixin_qrcode_info.get("fwh",""),
            "weixin_channel_code":"hby",
        })
        return {
            "fetched":fetched,
            "fetched_date":fetched_date,
            "reward_text":reward_text,
            "reward_type":reward_type,
            "is_bind": self.request.user.is_authenticated(),
            "friend_num":friend_num,
            "invite_experience_amount":invite_experience_amount,
            "inviter_head_url":inviter_head_url,
            "fphone": fphone,
            "original_id":weixin_qrcode_info.get("fwh",""),
            "weixin_channel_code":"hby",
        }

    def dispatch(self, request, *args, **kwargs):
        self.openid = self.request.session.get('openid')
        self.w_user = None
        if not self.openid:
            code = request.GET.get('code')
            state = request.GET.get('state')
            error_msg = ""
            if code and state:
                try:
                    account = WeixinAccounts.getByOriginalId(state)
                    request.session['account_key'] = account.key
                    oauth = WeChatOAuth(account.app_id, account.app_secret, )
                    user_info = oauth.fetch_access_token(code)
                    self.openid = user_info.get('openid')
                    request.session['openid'] = self.openid
                    self.w_user, old_subscribe = getOrCreateWeixinUser(self.openid, account)
                except WeChatException, e:
                    error_msg = e.message
            else:
                error_msg = u"code or state is None"
            if error_msg:
                return redirectToJumpPage(error_msg)
        else:
            self.w_user =WeixinUser.objects.filter(openid=self.openid).first()
        if self.w_user and self.w_user.user:
            if request.user.is_authenticated():
                if self.w_user.user == request.user:
                    return super(WechatShareTemplate, self).dispatch(request, *args, **kwargs)
            form = OpenidAuthenticationForm(self.openid, data=request.GET)
            if form.is_valid():
                auth_login(request, form.get_user())
            return super(WechatShareTemplate, self).dispatch(request, *args, **kwargs)
        else:
            if request.user.is_authenticated():
                logout(request)
            return super(WechatShareTemplate, self).dispatch(request, *args, **kwargs)

class FetchXunleiCardAward(APIView):
    permission_classes = (IsAuthenticated, )

    def getReward(self, type):
        with transaction.atomic():
            reward = Reward.objects.select_for_update().filter(type=type, is_used=False).first()
            if reward:
                reward.is_used = True
                reward.save()
            return reward

    def post(self, request):
        user = request.user
        activity = Activity.objects.filter(code="fkflr").first()
        if not activity:
            return Response({"ret_code": -1, "message":"没有该活动"})
        if activity.is_stopped:
            return Response({"ret_code": -1, "message":"活动已经截止"})
        now = timezone.now()
        if activity.start_at > now:
            return Response({"ret_code": -1, "message":"活动还未开始"})
        if activity.end_at < now:
            return Response({"ret_code": -1, "message":"活动已经结束"})
        type = request.POST.get('type')
        if not type or not type.isdigit() or int(type) not in (0, 1):
            return Response({"ret_code": -1, "message":"type error"})
        type = int(type)

        code = activity.code+"_"+str(type)
        activity_reward_record, _ = ActivityRewardRecord.objects.get_or_create(user=user, activity_code=code)
        if activity_reward_record.status:
            return Response({"ret_code": -1, "message":"您已经领取过"})

        w_user = WeixinUser.objects.filter(user=user).first()
        if not w_user:
            return Response({"ret_code": -1, "message":"请绑定服务号"})
        reward = None
        if type == 0:#bind vip card
            bind_action_record = WeiXinUserActionRecord.objects.filter(user_id=user.id, action_type='bind').first()
            create_time = local_to_utc(datetime.datetime.fromtimestamp(bind_action_record.create_time))
            if bind_action_record and create_time>=activity.start_at and create_time<=activity.end_at:
                reward = self.getReward("7天迅雷会员")
            else:
                return Response({"ret_code": -1, "message":"您不是首次绑定用户哦～"})
        if type == 1:#invest vip card
            p2pRecord = P2PRecord.objects.filter(user=request.user, catalog=u'申购').order_by("create_time").first()
            if p2pRecord and p2pRecord.create_time >=activity.start_at and p2pRecord.create_time<=activity.end_at and float(p2pRecord.amount)>=1000:
                reward = self.getReward("1年迅雷会员")
            else:
                return Response({"ret_code": -1, "message":"您不满足领取条件~"})
        if not reward:
            return Response({"ret_code": -1, "message":"奖品已经领完"})
        try:
            with transaction.atomic():
                record = ActivityRewardRecord.objects.select_for_update().get(id=activity_reward_record.id)
                if record.status:
                    reward.is_used=False
                    reward.save()
                    return Response({"ret_code": -1, "message":"您已经领取过"})
                record.activity_desc = 'xunleivip reward_id=%s'%reward.id
                record.status = True
                record.save()
        except Exception, e:
            reward.is_used=False
            reward.save()
            logger.debug(traceback.format_exc())
            return Response({"ret_code": -1, "message":"系统繁忙"})
        inside_message.send_one.apply_async(kwargs={
            "user_id": request.user.id,
            "title": reward.type,
            "content": reward.content,
            "mtype": "activity"
        })
        sentCustomerMsg.apply_async(kwargs={
            #奖励发放通知  奖励名称 奖品兑换码  会员有效期
                "txt":"奖励发放通知\n奖励名称：%s\n有效期至：%s\n兑换码：%s\n请在会员有效期内至迅雷会员官网进行兑换"%(reward.type, timezone.localtime(reward.end_time).strftime("%Y年%m月%d日"), reward.content), #\n兑换码:%s
                "openid":w_user.openid,
            },
                queue='celery02')
        return Response({"ret_code": 0, "message": '恭喜您，奖励领取成功～'})












