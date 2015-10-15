#-*- coding: utf-8 -*-
#########################################################################
# Author: Yihen Liu
# Created Time: 2015-09-09 13:23:07
# File Name: reward.py
# Description: 策划活动中的红包、奖品、加息券等用户奖励行为，独立在这个文件中
#########################################################################
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q
from datetime import datetime
from wanglibao_redpack import backends as redpack_backends
import inspect
import time
import json
import logging
from django.views.decorators.csrf import csrf_protect
from wanglibao_account import message as inside_message
from marketing.models import IntroducedBy, Reward
from wanglibao_reward.models import WanglibaoActivityGift, WanglibaoUserGift, WanglibaoActivityGiftGlobalCfg, WanglibaoWeixinRelative
from wanglibao_redpack.models import RedPackEvent
from wanglibao_activity.models import Activity, ActivityRule
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_p2p.models import P2PRecord
from misc.models import Misc
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from marketing.utils import get_user_channel_record
from django.conf import settings
logger = logging.getLogger('wanglibao_reward')

def ajax_response_reward(request):
    activity = request.POST.get("activity", "")
    action = request.POST.get("action", "")
    util = WanglibaoReward(request, activity)
    if action == "IS_VALID_USER":
        year = request.POST.get("year", 1970)
        month = request.POST.get("month", 1)
        day = request.POST.get("day", 1)
        return util.is_register_in_activity_period(year, month, day)

    if action == 'IS_VALID_CHANNEL':
        return util.is_valid_channel()

    if action == 'ENTER_WEB_PAGE':
        pass

    if action == 'GET_REDPACK':
        pass

    if action == 'GET_REWARD':
        pass

class WanglibaoReward(object):

    def __init__(self, request):
        self.request = request
        self.activity = None
        self.global_cfg = None

    def is_register_in_activity_period(self, year=1970, month=1, day=1):
        """
            判断用户是不是在活动期间内注册的新用户
        """
        create_at = int(time.mktime(self.request.user.date_joined.date().timetuple()))  # 用户注册的时间戳
        activity_start = time.mktime(datetime(year, month, day).timetuple())  # 活动开始时间

        if activity_start > create_at:
            to_json_response = {
                'ret_code': 3000,
                'message': u'非活动期注册用户',
            }
        else:
            to_json_response = {
                'ret_code': 3001,
                'message': u'活动期注册用户',
            }
        logger.debug("user_id:%d, check invite_code flow,ret_code:%d, message:%s " %(self.request.user.id, to_json_response["ret_code"], to_json_response["message"]))
        return HttpResponse(json.dumps(to_json_response), content_type='application/json' )

    def is_login(self):
        """
            判断用户是不是已经登录
        """
        if not self.request.user.is_authenticated():
            to_json_response = {
                'ret_code': 4000,
                'message': u'用户没有登陆，请先登陆',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    def is_valid_channel(self):
        """
            优先使用WanglibaoActivityGift的渠道配置
        """
        channels = WanglibaoActivityGift.objects.filter(activity=self.activity).first()
        if not channels:
            channels = Activity.objects.filter(code=self.activity).first()
            if not channels:
                to_json_response = {
                    'ret_code': 3000,
                    'message': u'全渠道',
                }
                return HttpResponse(json.dumps(to_json_response), content_type='application/json' )
            else:
                channels = channels.channel.split(",")
        else:
            channels = channels.channel.split(",")

        record = get_user_channel_record(self.request.user.id)
        if not record:
            to_json_response = {
                'ret_code': 3001,
                'message': u'非渠道用户',
            }
        else:
            if record.name not in channels:
                to_json_response = {
                    'ret_code': 3002,
                    'message': u'渠道用户不是从对应的渠道过来',
                }
            else:
                to_json_response = {
                    'ret_code': 3003,
                    'message': u'渠道用户从对应的渠道过来',
                }

        logger.debug("user_id:%d, check invite_code flow,ret_code:%d, message:%s " %(self.request.user.id, to_json_response["ret_code"], to_json_response["message"]))
        return HttpResponse(json.dumps(to_json_response), content_type='application/json' )

    def get_activity_rewards(self):
        """
            获得奖品的种类
        """
        rewards = WanglibaoActivityGift.objects.filter(activity=self.activity).values("name", "code", "count")
        return rewards

    def get_total_rewards(self, name):
        """
            获得单个奖品在gift表中总共有多少（包括待发和已发）
        """
        record = WanglibaoUserGift.objects.filter(Q(valid=0)|Q(valid=1), activity=self.activity, name=name).aggregate(counts=Count("id"))
        return record["counts"] if record else 0

    def get_reward_max_index(self, name):
        """
            获得奖品最大下标（包括待发和已发和无效）
        """
        record = WanglibaoUserGift.objects.filter(activity=self.activity).aggregate(counts=Count("id"))
        return record["counts"] if record else 0

    def get_used_rewards(self, name):
        """
            获得单个奖品已发多少
        """
        record = WanglibaoUserGift.objects.filter(activity__code__extra=self.activity, name=name, valid=0).aggregate(counts=Count("id"))
        return record["counts"] if record else 0

    def has_distributed_reward(self):
        """
            判断是否已经给用户在gift表中生成奖品
        """
        record = WanglibaoUserGift.objects.filter(user=self.request.user, activity=self.activity).aggregate(counts=Count('id'))

        return record['counts'] if record else 0

    def gift_is_valid(self, index, rate):
        if index % ((100/rate)-1) == 0:
            return True

        return False

    def distribute_one_reward(self, name, counts):
        gift = WanglibaoUserGift.objects.create(
            user=self.request.user,
            #rules=WanglibaoActivityGift.objects.filter(activity=self.activity, name=reward["name"]),
            activity=self.activity,
            index=self.get_reward_max_index()+1,
            name=name,
            valid=3,
        )
        has_send = self.get_used_rewards(name)
        if has_send < counts:
            if gift.rules.rate == 0:  # 0表示任意
                gift.valid = 0
                gift.save()
                return

            if self.gift_is_valid(gift.index, gift.rules.rate):
                gift.valid = 0
                gift.save()
            else:
                gift.valid = 1
                gift.save()
                #获得还有多少个奖品，每个奖品还有几个,还有多少次抽奖机会, 并将结果返回


    def distribute_rewards(self):
        """
            给用户预先在gift表中，将奖品生成
        """
        if not self.has_distributed_reward():
            rewards = self.get_activity_rewards()
            for reward in rewards:
                self.distribute_one_reward(reward["name"], reward["count"])

    def send_redpack(self):
        """
            发红包
        """
        try:
            dt = timezone.datetime.now()
            record = WanglibaoActivityGift.objects.filter(type=0, activity=self.activity)
            redpack_event = RedPackEvent.objects.filter(invalid=False, describe=record.code, give_start_at__lte=dt, give_end_at__gte=dt).first()
        except Exception, reason:
            logger.debug("send redpack Exception, msg:%s" % (reason,))
        else:
            gift = WanglibaoUserGift.objects.filter(type=0, rules=record, valid=0).first()
            gift.valid = 1
            gift.save()
        if redpack_event:
            redpack_backends.give_activity_redpack(self.request.user, redpack_event, 'pc')
        pass

    def send_reward(self):
        """
            发加息券,代金券等
        """
        gift_name = "None"
        now = timezone.now()
        reward = Reward.objects.filter(type=gift_name,
                                       is_used=False,
                                       end_time__gte=now).first()

        inside_message.send_one.apply_async(kwargs={
            "user_id": self.request.user.id,
            "title": reward.description,
            "content": reward.content,
            "mtype": "activity"
        })
        pass
    def ignore_request(self):
        """
            处理用户的不获奖行为
        """
        pass

class WeixinShareDetailView(TemplateView):
    template_name = 'app_weChatDetail.jade'

    def __init__(self):
        self.activity = None
        self.global_cfg = None

    @property
    def current_function_name(self):
        return inspect.stack()[1][3]

    def exception_msg(self, reason, msg=u'None'):
        logger.exception("class:%s, function:%s, reason,%s, msg:%s" %(self.__class__.__name__, self.current_function_name, reason, msg))

    def error_msg(self, msg=u'None'):
        logger.error("class:%s, function:%s, msg:%s" %(self.__class__.__name__, self.current_function_name, msg))

    def debug_msg(self, msg=u'None'):
        logger.debug("class:%s, function:%s,  msg:%s" %(self.__class__.__name__, self.current_function_name, msg))

    def has_combine_redpack(self, product_id, activity):
        """
            判断是否已经生成了此次活动的组合红包
        """
        if not self.activity:
           self.get_activity_by_id(activity)
        try:
            combine_redpack = WanglibaoActivityGift.objects.filter(gift_id=product_id, activity=self.activity)
        except Exception, reason:
            self.exception_msg(reason, u'判断组合红包生成报异常, gift_id:%s, activity:%s' %(product_id, self.activity))
        return True if combine_redpack else False

    def get_activity_by_id(self, activity_id):
        try:
            self.activity = Activity.objects.filter(code=activity_id).first()
        except Exception, reason:
            self.exception_msg(reason, u'获得activity的实体报异常')

    def get_redpack_id(self, activity):
        """
            根据活动管理配置，获得对应的红包配置信息
        """
        self.get_activity_by_id(activity)
        if self.activity:
            if self.activity.is_stopped:
                self.debug_msg(u'活动已经暂停了')
                return None
            try:
                activity_rules = ActivityRule.objects.filter(activity=self.activity)
            except Exception, reason:
                self.exception_msg(reason, u'获取活动规则失败')
                return None

            try:
                return [rule.redpack for rule in activity_rules]
            except Exception, reason:
                self.exception_msg(reason, u'获取红包编号失败')
                return None
        else:
            return None

    def get_redpack_by_id(self, ids):
        """
            根据传入的id集合（list），获得红包的信息
        """
        if type(ids) is not list:
            return None
        try:
            return RedPackEvent.objects.filter(id__in=ids)
        except Exception, reason:
            self.exception_msg(reason, u'获得配置的红包失败')
            return None

    def generate_combine_redpack(self, product_id, activity):
        """
            生成此次活动的组合红包
        """
        redpack_type = {
        "direct": 0,
        "interest_coupon": 1,
        "percent": 2}
        if not self.global_cfg:
            if not self.get_global_cfg(activity):
                self.throw_exception(u'对应的全局红包活动配置没有配，请先配置')

        if not self.has_combine_redpack(product_id, activity):
            ids = self.get_redpack_id(activity)
            if ids:
                redpacks = self.get_redpack_by_id(ids)
            else:
                self.debug_msg(u"获得配置红包id失败")
                return None
            self.debug_msg("红包编号为：%s" % (ids, ))
            for redpack in redpacks:
                try:
                    activity_gift = WanglibaoActivityGift.objects.create(
                    cfg=self.global_cfg,
                    gift_id=product_id,
                    activity=self.activity,
                    redpack=redpack,
                    name=redpack.rtype,
                    total_count=redpack.value,  #这个地方很关键,优惠券个数
                    valid=True
                    )
                    activity_gift.type = redpack_type[redpack.rtype]
                    activity_gift.save()
                    self.debug_msg("生成红包 %s 成功; 奖励类型:%s" % (redpack.id, redpack.rtype))
                except Exception, reason:
                    self.exception_msg(reason, '组合红包入库报错')

    def has_got_redpack(self, phone_num, activity, order_id, openid):
        """
            判断用户是否已经领完奖品了
        """
        if not self.activity:
            self.activity = self.get_activity_by_id(activity)
        try:
            user_gift = WanglibaoUserGift.objects.filter(rules__gift_id__exact=order_id, identity=(str(phone_num)), activity=self.activity).first()
            if not user_gift:
                logger.debug("没有从数据库里查到用户(%s)的领奖记录, openid:%s, order_id:%s" %(phone_num, openid, order_id))
            else:
                logger.debug("已经从数据库里查到用户(%s)的领奖记录, openid:%s, order_id:%s" %(phone_num, openid, order_id))
            return user_gift
        except Exception, reason:
            self.exception_msg(reason, u'判断用户领奖，数据库查询出错')
            return None

    def distribute_redpack(self, phone_num, openid, activity, product_id):
        """
            根据概率，分发奖品
        """
        if not self.activity:
            self.get_activity_by_id(activity)

        try:
            gifts = WanglibaoActivityGift.objects.filter(gift_id=product_id, activity=self.activity, valid=True)
            counts = gifts.count()
            #TODO：当多人并发的时候，会出现发多了(一个加息券发给了两个及多个人)；
            if counts == 0:
                gift = None
            else:
                index = int(time.time())%counts
                gift = gifts[index]

        except Exception, reason:
            self.exception_msg(reason, u'获得待发奖项抛异常')
            return None

        if gift:
            gift.valid = False
            gift.save()
            user_profile = WanglibaoUserProfile.objects.filter(phone=phone_num).first()
            sending_gift = WanglibaoUserGift.objects.create(
                rules=gift,
                user=user_profile.user if user_profile else None,
                identity=phone_num,
                activity=self.activity,
                amount=gift.redpack.amount,
                type=gift.type,
                valid=0,
            )
            sending_gift.save()
            logger.debug("生成发奖记录0:gift:%s, redpack:%s, redpack_amount:%s, redpack_describe:%s" %(gift, gift.redpack, gift.redpack.amount, gift.redpack.describe))
            invalid_gift = WanglibaoUserGift.objects.create(
                rules=gift,
                user=user_profile.user if user_profile else None,
                identity=openid,
                activity=self.activity,
                amount=gift.redpack.amount,
                type=gift.type,
                valid=2,
            )
            invalid_gift.save()
            logger.debug("生成发奖记录1:gift:%s, redpack:%s, redpack_amount:%s, redpack_describe:%s" %(gift, gift.redpack, gift.redpack.amount, gift.redpack.describe))
            if user_profile:
                if gift.redpack:
                    redpack_backends.give_activity_redpack(user_profile.user, gift.redpack, 'pc')
                    logger.debug("给用户 %s 发了红包，红包大小：%s, 红包组合是:%s, 购标订单号：%s" % (phone_num,gift.redpack.amount, activity, product_id))
                    sending_gift.valid = 1
                    sending_gift.save()

            return sending_gift
        else:
            return 'No Reward'

    def get_distribute_status(self, order_id, activity):
            """
                获得用户领奖信息
            """
            if not self.activity:
                self.get_activity_by_id(activity)

            try:
                gifts = WanglibaoUserGift.objects.filter(rules__gift_id__exact=order_id, activity=self.activity, valid__in=(0, 1)).all()
                return gifts
            except Exception, reason:
                self.exception_msg(reason, u'获取已领奖用户信息失败')
                return None

    def get_global_cfg(self, activity):
        """
            获得活动红包的全局配置信息
        """
        if not self.activity:
            self.get_activity_by_id(activity)

        try:
            self.global_cfg = WanglibaoActivityGiftGlobalCfg.objects.filter(activity=self.activity).get()
            return self.global_cfg
        except Exception, reason:
            self.exception_msg(reason, u'配置全局配置抛出异常, activity:%s' % (activity,))
            return None

    def is_valid_user_auth(self, order_id, activity):
        if not self.activity:
            self.get_activity_by_id(activity)

        if not self.global_cfg:
            self.get_global_cfg(activity)

        try:
            p2p_record = P2PRecord.objects.filter(order_id=order_id, amount__gte=self.global_cfg.amount)
            return p2p_record
        except Exception, reason:
            self.exception_msg(reason, u"判断用户投资额度抛异常")
            return None

    def get_react_text(self, index):
        text = [u'感谢土豪，加息券已到手！',
                u'这次，终于让我抢到啦！',
                u'哈哈，轻松一点，加息到手！',
                u'下次一定抢到2%加息券！',
                u'我去使用加息券喽，拜拜~',
                u'大家手气如何啊？！',
                u'太险了，差一点没抢到。',
                u'感谢土豪，带我飞。',
                u'投资就能发加息福袋啦？',
                u'土豪，传授下投资经验吧'
                ]
        return text[index]

    def format_response_data(self, gifts, types=None):
        if gifts == None:
            return None

        if types == 'alone':
            logger.debug("整理用户的数据返回前端，phone:%s" %(gifts.identity,))
            QSet = WanglibaoWeixinRelative.objects.filter(phone=gifts.identity).values("phone", "nick_name", "img", "openid").first()
            phone = WanglibaoUserGift.objects.filter(user=gifts.user, activity=gifts.activity, rules=gifts.rules).exclude(identity=QSet["openid"]).first().identity
            if QSet:
                ret_val = {"amount": gifts.amount, "name": QSet["nick_name"], "img": QSet["img"], "phone": phone}
            else:
                ret_val = {"amount": 0, "name": "", "img": "", "phone": ""}
            self.debug_msg('个人获奖信息返回前端:%s' % (ret_val,))
            return ret_val

        if types == 'gifts':
            user_info = {gift.identity: gift for gift in gifts}
            self.debug_msg("format_response_data, 已经领取的 奖品 的key值序列：%s" %(user_info.keys(),))
            QSet = WanglibaoWeixinRelative.objects.filter(phone__in=user_info.keys())
            weixins = {item.phone: item for item in QSet}
            self.debug_msg("format_response_data, 已经领取的 用户 的key值序列：%s" %(weixins.keys(),))
            ret_value = list()
            index = 0
            for key in weixins.keys():
                print user_info[key].amount
                print weixins[key].nick_name
                ret_value.append({"amount": user_info[key].amount,
                                  "time": user_info[key].get_time,
                                  "name": weixins[key].nick_name,
                                  "img": weixins[key].img,
                                  "message": self.get_react_text(index)})
                index += 1
            self.debug_msg('所有获奖信息返回前端:%s' % (ret_value,))
            return ret_value

    def update_weixin_wanglibao_relative(self, openid, phone_num):
        try:
            relative = WanglibaoWeixinRelative.objects.filter(openid=openid).first()
            old = None
            if relative:
                old = relative.phone
                relative.phone = phone_num
                relative.save()
                self.debug_msg("用户更新自己的手机号为:%s, openid:%s" %(phone_num, openid))
                return old
            else:
                self.debug_msg("待更新的微信网利宝用户关系记录为空")
                return None
        except Exception, reason:
            self.exception_msg(reason, "weixin-wanglibao-realitive table 更新用户的手机号报异常")
            return None

    def throw_exception(self, msg):
        raise Exception(msg)

    def get_context_data(self, **kwargs):
        openid = kwargs["openid"]
        phone_num = kwargs['phone_num']
        order_id = kwargs['order_id']
        activity = kwargs['activity']
        self.debug_msg("openid:%s, phone:%s, order_id:%s, activity:%s " % (openid, phone_num, order_id, activity))

        try:
            key = 'share_redpack'
            shareconfig = Misc.objects.filter(key=key).first()
            if shareconfig:
                shareconfig = json.loads(shareconfig.value)
                if type(shareconfig) == dict:
                    activitys=shareconfig['activity']
        except Exception, reason:
            logger.exception('get misc record exception, msg:%s' % (reason,))
            raise
        else:
            activitys = activitys.split(",")
            if len(activitys) == 0:
                self.throw_exception("Misc中, activity没有配置")

            index = int(time.time()) % len(activitys)
            try:
                record = WanglibaoActivityGift.objects.filter(gift_id=order_id).first()
            except Exception, reason:
                record = None
                self.exception_msg("获得activity报异常， order_id:%s" %(order_id,), reason)
            activity = record.activity.code if record else activitys[index]
            logger.debug("misc配置的activity有:%s, 本次使用的activity是：%s" % (activitys, activity))

        #更新用户的手机号
        old_phone = self.update_weixin_wanglibao_relative(openid, phone_num)

        if not self.has_combine_redpack(order_id, activity):
            self.generate_combine_redpack(order_id, activity)

        user_gift = self.has_got_redpack(old_phone, activity, order_id, openid)

        if not user_gift:
            self.debug_msg('phone:%s 没有领取过奖品' %(phone_num,) )
            with transaction.atomic():
                user_gift = self.distribute_redpack(phone_num, openid, activity, order_id)

            if "No Reward" == user_gift:
                self.debug_msg('奖品已经发完了，用户:%s 没有领到奖品' %(phone_num,))
                self.template_name = 'app_weChatEnd.jade'
                shareTitle, shareContent, url = get_share_infos(order_id)
                return {
                    "share":{'content':shareContent,'title':shareTitle, 'url':url}
                }
                #redirect_url = reverse('weixin_share_end')+'?url_id=%s'%order_id
                #return redirect(redirect_url)
        else:
            # 用户有可能更改了自己的手机，如果已经领取了，就更新为最新的手机号
            user_gift.identity = phone_num
            user_gift.save()
            self.debug_msg('phone:%s 已经领取过奖品, gift:%s' %(phone_num, user_gift, ))
        gifts = self.get_distribute_status(order_id, activity)
        shareTitle, shareContent, url = get_share_infos(order_id)
        return {
            "ret_code": 0,
            "self_gift": self.format_response_data(user_gift, 'alone'),
            "all_gift": self.format_response_data(gifts, 'gifts'),
             "share":{'content':shareContent,'title':shareTitle, 'url':url}
        }

    def dispatch(self, request, *args, **kwargs):
        key = 'share_redpack'
        is_open = False
        shareconfig = Misc.objects.filter(key=key).first()
        if shareconfig:
            shareconfig = json.loads(shareconfig.value)
            if type(shareconfig) == dict and shareconfig['is_open'] == 'true':
                is_open = True

        if not is_open:
            data = {
                'ret_code': 9010,
                'message': u'配置开关关闭，分享无效;',
            }
            return HttpResponse(json.dumps(data), content_type='application/json')
        return super(WeixinShareDetailView, self).dispatch(request, *args, **kwargs)

class WeixinShareEndView(TemplateView):
    template_name = 'app_weChatEnd.jade'

    def get_context_data(self, **kwargs):
        order_id = self.request.GET.get('url_id')
        shareTitle, shareContent, url = get_share_infos(order_id)
        logger.debug("抵达End页面，order_id:%s, URL:%s" %(order_id, url))
        return {
         "share":{'content':shareContent,'title':shareTitle, 'url':url}
        }


class WeixinShareStartView(TemplateView):
    template_name = 'app_weChatStart.jade'

    def is_valid_user_auth(self, order_id, amount):
        try:
            p2p_record = P2PRecord.objects.filter(order_id=order_id, amount__gte=amount)
            return p2p_record
        except Exception, reason:
            logger.exception(u"判断用户投资额度抛异常 %s" %(reason,) )

    def get_context_data(self, **kwargs):
        openid = self.request.GET.get('openid')
        order_id = self.request.GET.get('url_id')
        #nick_name = self.request.GET.get('nick_name')
        nick_name = self.request.session.get("nick_name")

        img_url = self.request.GET.get('head_img_url')
        record = WanglibaoWeixinRelative.objects.filter(openid=openid).first()

        if not record:
            logger.debug('入库微信授权信息, nick_name:%s, openid:%s, img:%s ' %(nick_name, openid, img_url))
            WanglibaoWeixinRelative.objects.create(
               openid=openid,
               nick_name=nick_name,
               img=img_url
            )
        else:
            logger.debug('微信授权信息很早就已经入库, nick_name:%s, openid:%s, img:%s ' %(nick_name, openid, img_url))
        shareTitle, shareContent, url = get_share_infos(order_id)
        return {
            'ret_code': 9001,
            'openid': openid,
            'order_id': order_id,
            'phone': record.phone if record else '',
            "share":{'content':shareContent,'title':shareTitle, 'url':url}
        }

    def dispatch(self, request, *args, **kwargs):
        openid = self.request.GET.get('openid')
        order_id = self.request.GET.get('url_id')
        amount = 1000
        account_id = 2
        key = 'share_redpack'
        is_open = False
        shareconfig = Misc.objects.filter(key=key).first()
        if shareconfig:
            shareconfig = json.loads(shareconfig.value)
            if type(shareconfig) == dict:
                amount = int(shareconfig['amount'])
                account_id = shareconfig['account_id']
                if shareconfig['is_open'] == 'true':
                    is_open = True
        if not is_open:
            data = {
                'ret_code': 9010,
                'message': u'配置开关关闭，分享无效;',
            }
            #TODO: 界面显示不友好
            return HttpResponse(json.dumps(data), content_type='application/json')

        if not self.is_valid_user_auth(order_id, amount) and False:
           data = {
                'ret_code': 9000,
                'message': u'用户投资没有达到%s元;' % (amount, ),
            }
           #TODO: 界面显示不友好
           return HttpResponse(json.dumps(data), content_type='application/json')
        if not openid:
            redirect_url = reverse('weixin_authorize_code')+'?url_id=%s&state=%s' % (order_id, account_id)
            print redirect_url
            return HttpResponseRedirect(redirect_url)#redirect(redirect_url)

        return super(WeixinShareStartView, self).dispatch(request, *args, **kwargs)

def get_share_infos(order_id):
    key = 'share_redpack'
    url = ""
    shareTitle=""
    shareContent=""
    shareconfig = Misc.objects.filter(key=key).first()
    if shareconfig:
        shareconfig = json.loads(shareconfig.value)
        if type(shareconfig) == dict:
            is_open = shareconfig.get('is_open', 'false')
            shareTitle=shareconfig.get('share_title', "")
            shareContent=shareconfig.get('share_content', "")
            url = settings.WEIXIN_CALLBACK_URL + reverse('weixin_share_order_gift')+"?url_id=%s"%order_id
    return shareTitle, shareContent, url