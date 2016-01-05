#-*- coding: utf-8 -*-
#########################################################################
# Author: Yihen Liu
# Created Time: 2015-09-09 13:23:07
# File Name: reward.py
# Description: 策划活动中的红包、奖品、加息券等用户奖励行为，独立在这个文件中
#########################################################################
from django.utils import timezone
from experience_gold.backends import SendExperienceGold
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Sum
from datetime import datetime
from wanglibao_account import message as inside_message
from wanglibao_redpack import backends as redpack_backends
import inspect
import time
import json
import logging
import random
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from django.shortcuts import redirect
from wanglibao.settings import CALLBACK_HOST
from wanglibao_account import message as inside_message
from marketing.models import IntroducedBy, Reward
from wanglibao import settings
from wanglibao_reward.models import WanglibaoActivityGift, WanglibaoUserGift, WanglibaoActivityReward, WanglibaoActivityGiftOrder
from wanglibao_redpack.models import RedPackEvent
from experience_gold.models import ExperienceEvent
from wanglibao_activity.models import Activity, ActivityRule
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_p2p.models import P2PRecord
from misc.models import Misc
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from marketing.utils import get_user_channel_record
from weixin.models import WeixinUser
import requests
from urllib import urlencode,quote

logger = logging.getLogger('wanglibao_reward')

class WeixinShareDetailView(TemplateView):
    template_name = 'app_weChatDetail.jade'

    def __init__(self):
        self.activity = None

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
                gift_id=product_id,
                activity=self.activity,
                redpack=redpack,
                name=redpack.rtype,
                total_count=redpack.value,  #这个地方很关键,优惠券个数
                valid=True,
                cfg_id=1
                )
                activity_gift.type = redpack_type[redpack.rtype]
                activity_gift.save()
                self.debug_msg("生成红包 %s 成功; 奖励类型:%s" % (redpack.id, redpack.rtype))
            except Exception, reason:
                self.exception_msg(reason, '组合红包入库报错')

        WanglibaoActivityGiftOrder.objects.create(
            valid_amount=len(redpacks),
            order_id=product_id
        )

    def has_got_redpack(self, phone_num, activity, order_id, openid):
        """
            判断用户是否已经领完奖品了
        """
        if not self.activity:
            self.activity = self.get_activity_by_id(activity)
        try:
            logger.debug("判断用户是否用此手机号在别的微信上领取过phone: %s, openid:%s, order_id:%s" %(phone_num, openid, order_id))
            award_user_gift = WanglibaoUserGift.objects.filter(rules__gift_id__exact=order_id, identity=str(phone_num), activity=self.activity).first()

            if not award_user_gift:  #用户这个手机号没有领取过，再判断这个微信号是否已经领取过
                user_gift = WanglibaoUserGift.objects.filter(rules__gift_id__exact=order_id, identity=str(openid), activity=self.activity).first()
                if not user_gift:
                    award_user_gift = None
                else:
                    award_user_gift = WanglibaoUserGift.objects.filter(rules=user_gift.rules, activity=self.activity).exclude(identity=(str(openid))).first()
                    logger.debug("已经从数据库里查到用户(%s)的领奖记录, openid:%s, order_id:%s" %(award_user_gift.identity, openid, order_id))
            return award_user_gift
        except Exception, reason:
            self.exception_msg(reason, u'判断用户领奖，数据库查询出错')
            return None

    def distribute_experience_glod(self, user, phone_num, openid, product_id, ex_event):
        gift_order = WanglibaoActivityGiftOrder.objects.select_for_update().filter(order_id=product_id).first()
        if gift_order.valid_amount <= 0:
            return "No Reward"
        else:
            gift = WanglibaoActivityGift.objects.create(
                gift_id=product_id,
                activity=self.activity,
                redpack_id=2,
                valid=True,
                type=3,
                cfg_id=1
            )
            logger.debug("在activity_gift表中增加了一条记录：体验金；product_id:%s, user_id:%s" % (product_id, user.id))

            send_gift = WanglibaoUserGift.objects.create(
                rules=gift,
                user=user if user else None,
                identity=phone_num,
                activity=self.activity,
                amount=ex_event.amount,
                type=gift.type,
                valid=0,
            )
            logger.debug("基于用户手机号的获奖记录已经生成; phone:%s, activity:%s, user_id:%s" % (phone_num, self.activity, user.id))

            WanglibaoUserGift.objects.create(
                rules=gift,
                user=user if user else None,
                identity=openid,
                activity=self.activity,
                amount=ex_event.amount,
                type=gift.type,
                valid=2,
            )
            logger.debug("基于用户微信openid的获奖记录已经生成了; phone:%s, activity:%s, user_id:%s" % (phone_num, self.activity, user.id))

            return send_gift

    @method_decorator(transaction.atomic)
    def distribute_redpack(self, phone_num, openid, activity, product_id):
        """
            根据概率，分发奖品
        """
        if not self.activity:
            self.get_activity_by_id(activity)

        profile = WanglibaoUserProfile.objects.filter(phone=phone_num).first()
        activity_record = WanglibaoActivityReward.objects.filter(order_id=product_id, user_id=profile.user.id, activity='weixin_experience_glod').first()
        if activity_record:
            return self.distribute_experience_glod(profile.user, phone_num, openid, product_id, activity_record.experience)

        try:
            #TODO: 增加分享记录表，用于计数和加锁
            #1: 此处有数据不一致性的问题, GiftOrder表和ActivityGift表的不一致性
            gift_order = WanglibaoActivityGiftOrder.objects.select_for_update().filter(order_id=product_id).first()
            if gift_order.valid_amount > 0:
                gifts = WanglibaoActivityGift.objects.filter(gift_id=product_id, activity=self.activity, valid=True)

                counts = gifts.count()
                if counts > 0:
                    if counts == 1:
                        index = 0
                    else:
                        index = random.randint(0, counts-1)
                    gift = gifts[index]
                    gift_order.valid_amount -= 1
                else:
                    gift = None
            else:
                gift = None

            gift_order.save()


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
                    # Modify by hb on 2015-12-14
                    #redpack_backends.give_activity_redpack_new(user_profile.user, gift.redpack, 'pc')
                    status, messege, redpack_record_id = redpack_backends.give_activity_redpack_new(user_profile.user, gift.redpack, 'pc')
                    if status:
                        logger.debug("=20151214= 给用户 %s 发了红包，红包大小：%s, 红包组合是:%s, 购标订单号：%s" % (phone_num, gift.redpack.amount, activity, product_id))
                        sending_gift.redpack_record_id = redpack_record_id
                    else:
                        logger.debug("=20151214= 给用户 %s 发红包失败[%s]，红包大小：%s, 红包组合是:%s, 购标订单号：%s" % (phone_num, messege, gift.redpack.amount, activity, product_id))
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
                # modify by hb on 2015-10-15 : 只查询微信号关联记录
                gifts = WanglibaoUserGift.objects.filter(rules__gift_id__exact=order_id, activity=self.activity, valid=2)
                exp_glods = gifts.filter(amount__gte=100)  #此处做了一个假设：加息券不可能大于100, 体验金不可能小于100
                counts = exp_glods.count() if exp_glods else 0
                return gifts.filter(amount__lt=10).all(), counts
            except Exception, reason:
                self.exception_msg(reason, u'获取已领奖用户信息失败')
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

    def format_response_data(self, gifts, openid, types=None):
        if gifts == None:
            return None

        if types == 'alone':
            logger.debug("整理用户的数据返回前端，phone:%s" %(gifts.identity,))
            QSet = WeixinUser.objects.filter(openid=openid).values("nickname", "headimgurl", "openid").first()
            if QSet:
                ret_val = {"amount": int(gifts.amount) if gifts.type == 3 else gifts.amount, "name": QSet["nickname"], "img": QSet["headimgurl"], "phone": gifts.identity}
            else:
                ret_val = {"amount": 0, "name": "", "img": "", "phone": ""}
            self.debug_msg('个人获奖信息返回前端:%s' % (ret_val,))
            return ret_val

        if types == 'gifts':
            user_info = {gift.identity: gift for gift in gifts}
            self.debug_msg("format_response_data, 已经领取的 奖品 的key值序列：%s" %(user_info.keys(),))
            QSet = WeixinUser.objects.filter(openid__in=user_info.keys())
            weixins = {item.openid: item for item in QSet}
            self.debug_msg("format_response_data, 已经领取的 用户 的key值序列：%s" %(weixins.keys(),))
            ret_value = list()
            index = 0
            for key in weixins.keys():
                ret_value.append({"amount": user_info[key].amount,
                                  "time": user_info[key].get_time,
                                  "name": weixins[key].nickname,
                                  "img": weixins[key].headimgurl,
                                  "message": self.get_react_text(index),
                                  "sort_by": int(time.mktime(time.strptime(str(user_info[key].get_time), '%Y-%m-%d %H:%M:%S+00:00')))})
                index += 1

            tmp_dict = {item["sort_by"]: item for item in ret_value}
            ret_value = [tmp_dict[key] for key in sorted(tmp_dict.keys(), reverse=True)]
            self.debug_msg('所有获奖信息返回前端:%s' % (ret_value,))
            return ret_value

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
                raise Exception("Misc中, activity没有配置")

            index = int(time.time()) % len(activitys)
            try:
                record = WanglibaoActivityGift.objects.filter(gift_id=order_id).first()
            except Exception, reason:
                record = None
                self.exception_msg("获得activity报异常， order_id:%s" %(order_id,), reason)
            activity = record.activity.code if record else activitys[index]
            logger.debug("misc配置的activity有:%s, 本次使用的activity是：%s" % (activitys, activity))

        if not self.has_combine_redpack(order_id, activity):
            self.generate_combine_redpack(order_id, activity)

        user_gift = self.has_got_redpack(phone_num, activity, order_id, openid)

        if not user_gift:
            self.debug_msg('phone:%s 没有领取过奖品' %(phone_num,) )
            has_gift = 'false'
            user_gift = self.distribute_redpack(phone_num, openid, activity, order_id)

            if "No Reward" == user_gift:
                self.debug_msg('奖品已经发完了，用户:%s 没有领到奖品' %(phone_num,))
                self.template_name = 'app_weChatEnd.jade'
                gifts, counts = self.get_distribute_status(order_id, activity)
                share_title, share_content, url = get_share_infos(order_id)
                return {
                    "count": counts,
                    "share": {'content': share_content, 'title': share_title, 'url': url},
                    "all_gift": self.format_response_data(gifts, openid, 'gifts'),
                }
        else:
            if phone_num == user_gift.identity:
                has_gift = 'false'
            else:
                has_gift = 'true'
            self.debug_msg('openid:%s (phone:%s) 已经领取过奖品, gift:%s' %(openid, user_gift.identity, user_gift, ))
        gifts, counts = self.get_distribute_status(order_id, activity)
        share_title, share_content, url = get_share_infos(order_id)
        return {
            "ret_code": 0,
            "count": counts,
            "has_gift": has_gift,
            "self_gift": self.format_response_data(user_gift, openid, 'alone'),
            "all_gift": self.format_response_data(gifts, openid, 'gifts'),
            "share": {'content': share_content, 'title': share_title, 'url': url}
        }

    def is_valid_user_auth(self, order_id, amount):
        try:
            p2p_record = P2PRecord.objects.filter(order_id=order_id, amount__gte=amount)
            return p2p_record
        except Exception, reason:
            logger.exception(u"判断用户投资额度抛异常 %s, order_id:%s, amount:%s " %(reason, order_id, amount) )

    def dispatch(self, request, *args, **kwargs):
        key = 'share_redpack'
        order_id = kwargs['order_id']
        is_open = False
        shareconfig = Misc.objects.filter(key=key).first()
        amount = 1000

        if shareconfig:
            shareconfig = json.loads(shareconfig.value)
            if type(shareconfig) == dict:
                amount = int(shareconfig['amount'])
                if shareconfig['is_open'] == 'true':
                    is_open = True

        if not is_open:
            data = {
                'ret_code': 9010,
                'message': u'配置开关关闭，分享无效;',
            }
            return HttpResponse(json.dumps(data), content_type='application/json')

        if not self.is_valid_user_auth(order_id, amount):
            data = {
                'ret_code': 9000,
                'message': u'用户投资没有达到%s元;' % (amount, ),
            }
            #TODO: 界面显示不友好
            return HttpResponse(json.dumps(data), content_type='application/json')

        return super(WeixinShareDetailView, self).dispatch(request, *args, **kwargs)


class WeixinShareTools(APIView):
    permission_classes = ()
    def __init__(self):
        self.activity = None

    def get_activity_by_id(self, activity_id):
        try:
            self.activity = Activity.objects.filter(code=activity_id).first()
        except Exception, reason:
            logger.debug(reason, u'获得activity的实体报异常')

    def has_got_redpack(self, phone_num, activity, order_id, openid):
        """
            判断用户是否已经领完奖品了
        """
        if not self.activity:
            self.activity = self.get_activity_by_id(activity)
        try:
            logger.debug("开奖页面，判断用户是否用此手机号在别的微信上领取过phone: %s, openid:%s, order_id:%s" %(phone_num, openid, order_id))
            award_user_gift = WanglibaoUserGift.objects.filter(rules__gift_id__exact=order_id, identity=str(phone_num)).first()

            if not award_user_gift:  #用户这个手机号没有领取过，再判断这个微信号是否已经领取过
                logger.debug(u'用户没有用手机号(%s)领取过' % (phone_num,))
                user_gift = WanglibaoUserGift.objects.filter(rules__gift_id__exact=order_id, identity=str(openid)).first()
                if not user_gift:
                    logger.debug(u'用户没有用此微信号(%s)领取过, order:%s' % (openid,order_id,))
                    award_user_gift = None
                else:
                    award_user_gift = WanglibaoUserGift.objects.filter(rules=user_gift.rules).exclude(identity=(str(openid))).first()
                    logger.debug("开奖页面，已经从数据库里查到用户(%s)的领奖记录, openid:%s, order_id:%s" %(award_user_gift.identity, openid, order_id))
            return award_user_gift
        except Exception, reason:
            logger.debug(u'判断用户领奖，数据库查询出错, reason:%s' % reason)
            return None

    def post(self, request):
        openid = request.DATA.get("openid")
        phone_num = request.DATA.get('phone_num')
        order_id = request.DATA.get('order_id')
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
                raise Exception("Misc中, activity没有配置")

            index = int(time.time()) % len(activitys)
            try:
                record = WanglibaoActivityGift.objects.filter(gift_id=order_id).first()
            except Exception, reason:
                record = None
                logger.exception("获得activity报异常， order_id:%s" %(order_id,), reason)
            activity = record.activity.code if record else activitys[index]
            logger.debug("misc配置的activity有:%s, 本次使用的activity是：%s" % (activitys, activity))

        user_gift = self.has_got_redpack(phone_num, activity, order_id, openid)
        if user_gift:
            to_json_response = {
                'has_gift': 'true',
                'message': u"用户已经领取过奖品"
            }
            logger.debug(u"开奖页面，返回前端：%s" % (to_json_response, ))
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')
        else:
            to_json_response = {
                'has_gift': 'false',
                'message': u"用户没有领取过奖品"
            }
            logger.debug(u"开奖页面，返回前端：%s" % (to_json_response, ))
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')


class WeixinShareEndView(TemplateView):
    template_name = 'app_weChatEnd.jade'

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

    def get_distribute_status(self, order_id):
        """
            获得用户领奖信息
        """
        try:
            gifts = WanglibaoUserGift.objects.filter(rules__gift_id__exact=order_id, valid=2)
            exp_glods = gifts.filter(amount__gte=100)  #此处做了一个假设：加息券不可能大于100, 体验金不可能小于100
            counts = exp_glods.count() if exp_glods else 0
            return gifts.filter(amount__lt=10).all(), counts
        except Exception, reason:
            logger.debug(reason, u'获取已领奖用户信息失败')
            return None
    def format_response_data(self, gifts):
        if gifts == None:
            return None

        user_info = {gift.identity: gift for gift in gifts}
        logger.debug("format_response_data, 已经领取的 奖品 的key值序列：%s" %(user_info.keys(),))
        QSet = WeixinUser.objects.filter(openid__in=user_info.keys())
        weixins = {item.openid: item for item in QSet}
        logger.debug("format_response_data, 已经领取的 用户 的key值序列：%s" %(weixins.keys(),))
        ret_value = list()
        index = 0
        for key in weixins.keys():
            ret_value.append({"amount": user_info[key].amount,
                              "time": user_info[key].get_time,
                              "name": weixins[key].nickname,
                              "img": weixins[key].headimgurl,
                              "message": self.get_react_text(index),
                              "sort_by": int(time.mktime(time.strptime(str(user_info[key].get_time), '%Y-%m-%d %H:%M:%S+00:00')))})
            index += 1

        tmp_dict = {item["sort_by"]: item for item in ret_value}
        ret_value = [tmp_dict[key] for key in sorted(tmp_dict.keys(), reverse=True)]
        logger.debug('所有获奖信息返回前端:%s' % (ret_value,))
        return ret_value

    def get_context_data(self, **kwargs):
        order_id = self.request.GET.get('url_id')
        share_title, share_content, url = get_share_infos(order_id)
        gifts, counts = self.get_distribute_status(order_id)
        logger.debug("抵达End页面，order_id:%s, URL:%s" %(order_id, url))
        return {
         "count": counts,
         "all_gift": self.format_response_data(gifts),
         "share": {'content': share_content, 'title': share_title, 'url': url}
        }


class WeixinShareStartView(TemplateView):
    template_name = 'app_weChatStart.jade'

    def is_valid_user_auth(self, order_id, amount):
        try:
            p2p_record = P2PRecord.objects.filter(order_id=order_id, amount__gte=amount)
            return p2p_record
        except Exception, reason:
            logger.exception(u"判断用户投资额度抛异常 %s, order_id:%s, amount:%s " %(reason, order_id, amount) )

    def get_context_data(self, **kwargs):
        openid = self.request.GET.get('openid')
        order_id = self.request.GET.get('url_id')

        user_gift = WanglibaoUserGift.objects.filter(identity=openid,).last()
        record = WanglibaoUserGift.objects.filter(rules=user_gift.rules).exclude(identity=(str(openid))).first() if user_gift else None
        logger.debug("start页面，openid 是:%s" % (openid,))
        share_title, share_content, url = get_share_infos(order_id)
        return {
            'ret_code': 9001,
            'openid': openid,
            'order_id': order_id,
            'phone': record.identity if record else '',
            "share": {'content': share_content, 'title': share_title, 'url': url}
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

        if not self.is_valid_user_auth(order_id, amount):
           data = {
                'ret_code': 9000,
                'message': u'用户投资没有达到%s元;' % (amount, ),
            }
           #TODO: 界面显示不友好
           return HttpResponse(json.dumps(data), content_type='application/json')


        redirect_uri = CALLBACK_HOST + reverse("weixin_share_order_gift")
        count = 0
        for key in request.GET.keys():
            if key == u'openid':
                continue
            if count == 0:
                redirect_uri += '?%s=%s'%(key, request.GET.get(key))
            else:
                redirect_uri += "&%s=%s"%(key, request.GET.get(key))
            count += 1
        redirect_uri = quote(redirect_uri)

        if openid:
            w_user = WeixinUser.objects.filter(openid=openid).first()

        if not openid or not w_user:
            redirect_url = reverse('weixin_authorize_code')+'?state=%s&redirect_uri=%s' % (account_id, redirect_uri)
            # print redirect_url
            return HttpResponseRedirect(redirect_url)#redirect(redirect_url)

        if not w_user.nickname:
            res = requests.request(
                    method='get',
                    url=CALLBACK_HOST + reverse('weixin_get_user_info')+'?openid=%s'%openid,#settings.WEIXIN_CALLBACK_URL+
                )
            result = res.json()
            if result.get('errcode'):
                redirect_url = reverse('weixin_authorize_code')+'?state=%s&auth=1&redirect_uri=%s' % (account_id, redirect_uri)
                logger.debug("获取微信用户信息出错:%s" % (result.get('errcode')),)
                # print redirect_url
                return HttpResponseRedirect(redirect_url)#redirect(redirect_url)
            else:
                nick_name = result.get('nickname')
                self.request.session['nick_name'] = nick_name

        try:
             user_gift = WanglibaoUserGift.objects.filter(rules__gift_id=order_id, identity=openid,).first()
             logger.debug("用户抽奖信息是：%s" % (user_gift,))

             if user_gift:
                 ano_gift = WanglibaoUserGift.objects.filter(rules=user_gift.rules).exclude(identity=(str(openid))).first()
                 logger.debug("openid:%s, phone:%s, product_id:%s,用户已经存在了，直接跳转页面" %(openid, ano_gift.identity, order_id,))
                 return redirect("/weixin_activity/share/%s/%s/%s/share/" %(ano_gift.identity, openid, order_id))

             QSet = WanglibaoActivityGift.objects.filter(gift_id=order_id)
             counts = QSet.count()
             left_counts = QSet.filter(valid=True).count()
             if left_counts == 0 and counts > 0:
                 return redirect("/weixin_activity/share/end/?url_id=%s" % (order_id,))

        except Exception, e:
            logger.exception("share-start-view dispatch 跳转的时候报异常")

        return super(WeixinShareStartView, self).dispatch(request, *args, **kwargs)

def get_share_infos(order_id):
    key = 'share_redpack'
    url = ""
    share_title = ""
    share_content = ""
    shareconfig = Misc.objects.filter(key=key).first()
    if shareconfig:
        shareconfig = json.loads(shareconfig.value)
        if type(shareconfig) == dict:
            share_title = shareconfig.get('share_title', "")
            share_content = shareconfig.get('share_content', "")
            url = CALLBACK_HOST + reverse('weixin_share_order_gift')+"?url_id=%s"%order_id
    return share_title, share_content, url


class WeixinRedPackView(APIView):
    permission_classes = ()

    def post(self, request, phone):
        key = 'share_redpack'
        shareconfig = Misc.objects.filter(key=key).first()
        if shareconfig:
            shareconfig = json.loads(shareconfig.value)
            if type(shareconfig) == dict:
                is_attention = shareconfig.get('is_attention', '')
                attention_code = shareconfig.get('attention_code', '')

        if not is_attention:
            data = {
                'ret_code': 9000,
                'message': u'配置开关关闭，无法关注;',
            }
            return HttpResponse(json.dumps(data), content_type='application/json')

        day = time.strftime("%Y-%m-%d", time.localtime())
        if day < "2015-11-23" or day > "2015-11-29":
            data = {
                'ret_code': 9100,
                'message': u'感恩节活动期已过，不发了',
            }
            return HttpResponse(json.dumps(data), content_type='application/json')

        phone_number = phone.strip()
        redpack = WanglibaoUserGift.objects.filter(get_time__gte="2015-11-23", get_time__lte="2015-11-29", identity=phone, activity__code=attention_code).first()
        if redpack:
            data = {
                'ret_code': 0,
                'message': u'用户已经领取了加息券',
                'amount': redpack.amount,
                'phone': phone_number
            }
            return HttpResponse(json.dumps(data), content_type='application/json')

        else:
            activity = Activity.objects.filter(code=attention_code).first()
            redpack = WanglibaoUserGift.objects.create(
                identity=phone_number,
                activity=activity,
                rules=WanglibaoActivityGift.objects.first(),#随机初始化一个值
                type=1,
                valid=0
            )

            user = WanglibaoUserProfile.objects.filter(phone=phone_number).first().user
            if user:
                try:
                    redpack_id = ActivityRule.objects.filter(activity=activity).first().redpack
                except Exception, reason:
                    logger.debug("从ActivityRule中获得redpack_id抛异常, reason:%s" % (reason, ))

                try:
                    redpack_event = RedPackEvent.objects.filter(id=redpack_id).first()
                except Exception, reason:
                    logger.debug("从RedPackEvent中获得配置红包报错, reason:%s" % (reason, ))

                try:
                    logger.debug("给用户 %s 发送红包 %s" % (user, redpack_event))
                    redpack_backends.give_activity_redpack(user, redpack_event, 'pc')
                except Exception, reason:
                    logger.debug("给用户发红包抛异常, reason:%s, msg: %s" % (reason,))
                else:
                    redpack.user = user
                    redpack.valid = 1
                    redpack.save()
                    data = {
                        'ret_code': 1000,
                        'message': u'下发加息券成功',
                        'amount': redpack.amount,
                        'phone': phone_number
                    }
                    return HttpResponse(json.dumps(data), content_type='application/json')


class RewardDistributer(object):
    """
        Description:发奖总入口
    """
    def __init__(self, request, kwargs):
        logger.debug("request:%s, kwargs:%s" % (request, kwargs))
        self.request = request
        self.kwargs = kwargs
        self.Processor = {
            ThanksGivenRewardDistributer: ('all',),
        }

    @property
    def activity(self):
        return 'all'
        #return self.request.DATA.get('activity', 'all')

    @property
    def processors(self):
        processor = []
        for key, value in self.Processor.items():
            if self.activity in value:
                processor.append(key)
        return processor

    def processor_for_distribute(self):
        for processor in self.processors:
            processor(self.request, self.kwargs).distribute()


class ThanksGivenRewardDistributer(RewardDistributer):
    def __init__(self, request, kwargs):
        super(ThanksGivenRewardDistributer, self).__init__(request, kwargs)
        self.amount = kwargs['amount']
        self.order_id = kwargs['order_id']
        self.user = kwargs['user']
        self.token = 'thanks_given'

    @property
    def is_valid(self):
        """
           用来标示次活动是否继续启用, 配合MISC使用, 如果不使用，
           只要将self.token对应的值从misc.activities中去掉即可
        """
        key = 'activities'
        activities = Misc.objects.filter(key=key).first()
        if activities:
            activities = json.loads(activities.value)
            if type(activities) == dict:
                activities = activities.get('valid_activity', '')
        logger.debug("activitys:%s, token:%s" % (activities, self.token))
        return True if activities.find(self.token)>=0 else False

    @property
    def reward(self):
        from wanglibao_reward.settings import thanks_given_rewards as rewards
        for key, values in rewards.items():
            if self.amount>=values[0] and self.amount<values[1]:
                if key == u'一年迅雷会员':
                    xunlei_reward = WanglibaoActivityReward.objects.filter(redpack_event__name=key, activity=u'ThanksGiven').count()
                    if xunlei_reward>=1000:
                        return u'感恩节1.5%加息券'
                return key

    def distribute(self):
        if not self.is_valid:
            return

        redpack_event = None
        reward = None
        if self.reward.find(u"红包") >=0 or self.reward.find(u'加息券')>=0:
            redpack_event = RedPackEvent.objects.filter(name=self.reward).first()
        else:
            reward = Reward.objects.filter(type=self.reward, is_used=False).first()
        user = self.request.user if self.request else self.user  #对于自动投标的用户，request参量为空
        logger.debug("用户(%s)的投资额度是：%s, 订单号：%s, 获得的红包是：%s, redpack_event:%s, reward:%s" % (user, self.amount, self.order_id, self.reward, redpack_event, reward,))
        try:
            WanglibaoActivityReward.objects.create(
                activity=u'ThanksGiven',
                user=user,
                order_id=self.order_id,
                redpack_event=redpack_event if redpack_event else None,
                reward=reward if reward else None,
                join_times=1,
                left_times=1,
                when_dist=1,
                has_sent=False,
                p2p_amount=self.amount,
                channel="all",
            )


        except Exception, reason:
            logger.debug("中奖信息入库报错:%s" % reason)

class DistributeRewardAPIView(APIView):
    """
        Description:抽奖总入口
    """
    permission_classes = ()

    def __init__(self):
        super(DistributeRewardAPIView, self).__init__()
        self.processors = [ThanksGivingDistribute, ]

    def post(self, request):
        self.activity = request.DATA.get('activity', '')
        run = None
        for processor in self.processors:
            if processor().token == self.activity:
                run = True
                break

        if run:
            return processor().distribute(request)
        else:
            json_to_response = {
                'ret_code': 3000,
                'message': u'接口还没有实现，请联系相应后端同学'
            }

            return HttpResponse(json.dumps(json_to_response), content_type="application/json")


class ActivityRewardDistribute(object):
    def __init__(self):
        self.token = ''  #用户从前端传入的activity(POST/GET)
        pass

    def distribute(self):
        """抽奖接口，必须被实现
        """
        raise NotImplementedError(u"抽象类中的方法，子类中需要被实现")


class ThanksGivingDistribute(ActivityRewardDistribute):
    def __init__(self):
        super(ThanksGivingDistribute, self).__init__()
        self.token = 'thanks_given'


    def is_first(self, request):
        reward = WanglibaoActivityReward.objects.filter(user=request.user, activity='ThanksGiven').first()
        if reward and reward.left_times == reward.join_times:
            return True
        else:
            return False

    def distribute(self, request):
        action = request.DATA.get('action', 'GET_REWARD_INFO')

        if action == "GET_REWARD":
            rewards = WanglibaoActivityReward.objects.filter(p2p_amount__gte=5000, activity="ThanksGiven", has_sent=True).all()
            phone = [reward.user.wanglibaouserprofile.phone for reward in rewards]
            reward = [reward.redpack_event.name for reward in rewards if reward.redpack_event] + [reward.reward.description for reward in rewards if reward.reward]
            json_to_response = {
                "phone": phone,
                "rewards": reward,
                "message": u'中奖名单',
                "ret_code": 4000
            }

            return HttpResponse(json.dumps(json_to_response), content_type='application/json')

        if not request.user.is_authenticated():
            json_to_response = {
               'ret_code': 1000,
                'message': u'用户没有登录'
            }

            return HttpResponse(json.dumps(json_to_response), content_type='application/json')


        level = request.DATA.get('level', "5000+")
        if level == "5000+":
            sum_reward = WanglibaoActivityReward.objects.filter(user=request.user, activity='ThanksGiven', p2p_amount__gte=5000).aggregate(left_sum=Sum('left_times'))
        elif level == "5000-":
            sum_reward = WanglibaoActivityReward.objects.filter(user=request.user, activity='ThanksGiven', p2p_amount__lt=5000).aggregate(left_sum=Sum('left_times'))
        if 'GET_REWARD_INFO' == action:
            json_to_response = {
                'ret_code': 1001,
                'message': u'获得用户的抽奖汇总信息',
                'left': sum_reward["left_sum"] if sum_reward['left_sum'] else 0  #用户可能从没有投过资
            }
            return HttpResponse(json.dumps(json_to_response), content_type='application/json')

        if 'POINT_AT' == action:

            if level == "5000+":
                reward = WanglibaoActivityReward.objects.filter(user=request.user, activity='ThanksGiven', left_times__gt=0, has_sent=False, p2p_amount__gte=5000).first()
            elif level == "5000-":
                reward = WanglibaoActivityReward.objects.filter(user=request.user, activity='ThanksGiven', left_times__gt=0, has_sent=False, p2p_amount__lt=5000).first()

            reward_name = None
            if reward:
                with transaction.atomic():
                    reward = WanglibaoActivityReward.objects.select_for_update().filter(pk=reward.id).first()
                    if reward.left_times == reward.when_dist:
                        """发站内信"""
                        if reward.reward:
                            # modify by hb on 2015-11-23
                            old_reward = Reward.objects.filter(pk=reward.reward.id).first()
                            if old_reward and old_reward.is_used:
                                new_reward = Reward.objects.filter(type=old_reward.type, is_used=False).order_by('-id').first()
                                reward.reward = new_reward
                            inside_message.send_one.apply_async(kwargs={
                                "user_id": request.user.id,
                                "title": reward.reward.type,
                                "content": reward.reward.content,
                                "mtype": "activity"
                            })
                            reward.reward.is_used = True
                            reward.reward.save()
                            reward_name = reward.reward.type

                        """发红包"""
                        if reward.redpack_event:
                            redpack_backends.give_activity_redpack(request.user, reward.redpack_event, 'pc')
                            reward_name = reward.redpack_event.name
                    json_to_response = {
                        'ret_code': 2000,
                        'message': u'用户抽奖信息描述',
                        'reward': reward_name,
                        'left': sum_reward["left_sum"]-1 if sum_reward['left_sum'] else 1,  #用户可能从没有投过资
                        'is_first': self.is_first(request)
                    }

                    reward.left_times -= 1
                    if reward.left_times<0:
                        reward.left_times=0
                    reward.has_sent = True
                    reward.save()
            else:
                json_to_response = {
                    'ret_code': 2001,
                    'message': u'用户抽奖机会已经用完了',
                    'reward': None,
                    'left': 0
                }

            return HttpResponse(json.dumps(json_to_response), content_type='application/json')


class XunleiActivityAPIView(APIView):
    permission_classes = ()

    def __init__(self):
        super(XunleiActivityAPIView, self).__init__()
        self.activity_name = 'xunlei_laba'

    def introduced_by_with(self, user_id, promo_token, register_time=None):
        """
            register_time:为None表示不需要关注用户的注册时间
        """
        if not register_time:
            introduced_by = IntroducedBy.objects.filter(user_id=user_id, channel__code=promo_token).first()
        else:
            introduced_by = IntroducedBy.objects.filter(user_id=user_id, channel__code=promo_token, created_at__gte=register_time).first()
        return True if introduced_by else False

    def has_generate_reward_activity(self, user_id, activity):
        activitys = WanglibaoActivityReward.objects.filter(user_id=user_id, activity=activity)
        return activitys if activitys else None

    def generate_reward_activity(self, user):
        """这个函数必须被不断重写
            三次摇奖必中两次，中将金额 分别为88(60%), 188(30%), 888(10%)
        """
        points = {
            "0-1-3-5-7-9": ("xunlei_laba_88", 88),
            "4-6-8": ("xunlei_laba_188", 188),
            "2": ("xunlei_laba_888", 888)
        }

        for index in xrange(2):
            records = WanglibaoActivityReward.objects.filter(activity=self.activity_name)
            counter = (records.count()+1) % 10
            for key, value in points.items():
                if str(counter) in key:
                    WanglibaoActivityReward.objects.create(
                    user=user,
                    experience=ExperienceEvent.objects.filter(name=value[0]).first(),
                    activity=self.activity_name,
                    when_dist=1,
                    left_times=1,
                    join_times=1,
                    channel='xunlei9',
                    has_sent=False,
                    p2p_amount=value[1]
                    )
                    break

        WanglibaoActivityReward.objects.create(
            user=user,
            experience=None,
            activity=self.activity_name,
            when_dist=1,
            left_times=1,
            join_times=1,
            channel='xunlei9',
            has_sent=False,
            p2p_amount=0
        )

        return WanglibaoActivityReward.objects.filter(user=user, activity=self.activity_name)

    def get(self, request):
        _type = request.GET.get("type", None)
        if _type == "orders":
            records = WanglibaoActivityReward.objects.filter(activity=self.activity_name, p2p_amount__gt=0, left_times=0)
            data = [{'phone': record.user.wanglibaouserprofile.phone, 'awards': str(record.p2p_amount)} for record in records]
            to_json_response = {
                'ret_code': 1005,
                'data': data,
                'message': u'获得抽奖成功用户',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

        if _type == "chances":
            if not request.user.is_authenticated():
                json_to_response = {
                    'code': 1000,
                    'message': u'用户没有登录'
                }

                return HttpResponse(json.dumps(json_to_response), content_type='application/json')

            if not self.introduced_by_with(request.user.id, 'xunlei9', "2015-12-29"):
                json_to_response = {
                    'code': 1005,
                    'lefts': 0,
                    'message': u'用户不是在活动期内从迅雷渠道过来的用户'
                }
                return HttpResponse(json.dumps(json_to_response), content_type='applicaton/json')

            if not self.has_generate_reward_activity(request.user.id, self.activity_name):
                self.generate_reward_activity(request.user)

            sum_left = WanglibaoActivityReward.objects.filter(activity=self.activity_name, user=request.user).aggregate(amount_sum=Sum('left_times'))
            to_json_response = {
                'ret_code': 1005,
                'lefts': str(sum_left["amount_sum"]) if sum_left else 0,
                'message': u'获得剩余抽奖次数',
            }
            return HttpResponse(json.dumps(to_json_response), content_type='application/json')

    def post(self, request):
        if not request.user.is_authenticated():
            json_to_response = {
                'code': 1000,
                'message': u'用户没有登录'
            }

            return HttpResponse(json.dumps(json_to_response), content_type='application/json')

        if not self.introduced_by_with(request.user.id, 'xunlei9', "2015-12-29"):
            json_to_response = {
                'code': 1001,
                'message': u'用户不是在活动期内从迅雷渠道过来的用户'
            }
            return HttpResponse(json.dumps(json_to_response), content_type='applicaton/json')

        _activitys = self.has_generate_reward_activity(request.user.id, self.activity_name)
        activitys = _activitys if _activitys else self.generate_reward_activity(request.user)
        activity_record = activitys.filter(left_times__gt=0)

        if activity_record.filter(left_times__gt=0).count() == 0:
            json_to_response = {
                'code': 1002,
                'messge': u'用户的抽奖机会已经用完了',
            }
            return HttpResponse(json.dumps(json_to_response), content_type='application/json')
        else:
            with transaction.atomic():
                record = WanglibaoActivityReward.objects.select_for_update().filter(pk=activity_record.first().id, has_sent=False).first()
                sum_left = WanglibaoActivityReward.objects.filter(activity=self.activity_name, user=request.user, has_sent=False).aggregate(amount_sum=Sum('left_times'))
                if record.experience:
                    json_to_response = {
                        'code': 0,
                        'lefts': sum_left["amount_sum"]-1,
                        'amount': "%04d" % (record.experience.amount,),
                        'message': u'用户抽到奖品'
                    }
                    SendExperienceGold(request.user).send(record.experience.id)

                else:
                    json_to_response = {
                        'code': 1,
                        'lefts': sum_left["amount_sum"]-1,
                        'message': u'此次没有得到奖品'
                    }

                record.left_times = 0
                record.has_sent = True
                record.save()
            return HttpResponse(json.dumps(json_to_response), content_type='application/json')
