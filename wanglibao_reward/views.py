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
import random
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from django.shortcuts import redirect
from wanglibao.settings import CALLBACK_HOST
from wanglibao_account import message as inside_message
from marketing.models import IntroducedBy, Reward
from wanglibao_reward.models import WanglibaoActivityGift, WanglibaoUserGift, WanglibaoActivityGiftGlobalCfg, WanglibaoWeixinRelative, WanglibaoActivityGiftOrder
from wanglibao_redpack.models import RedPackEvent
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
                    award_user_gift = WanglibaoUserGift.objects.filter(rules__gift_id__exact=order_id, activity=self.activity).exclude(identity=(str(openid))).first()
                    logger.debug("已经从数据库里查到用户(%s)的领奖记录, openid:%s, order_id:%s" %(award_user_gift.identity, openid, order_id))
            return award_user_gift
        except Exception, reason:
            self.exception_msg(reason, u'判断用户领奖，数据库查询出错')
            return None

    @method_decorator(transaction.atomic)
    def distribute_redpack(self, phone_num, openid, activity, product_id):
        """
            根据概率，分发奖品
        """
        if not self.activity:
            self.get_activity_by_id(activity)

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
                # modify by hb on 2015-10-15 : 只查询微信号关联记录
                gifts = WanglibaoUserGift.objects.filter(rules__gift_id__exact=order_id, activity=self.activity, valid=2).all()
                return gifts
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
                ret_val = {"amount": gifts.amount, "name": QSet["nickname"], "img": QSet["headimgurl"], "phone": gifts.identity}
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
                gifts = self.get_distribute_status(order_id, activity)
                share_title, share_content, url = get_share_infos(order_id)
                return {
                    "share": {'content': share_content, 'title': share_title, 'url': url},
                    "all_gift": self.format_response_data(gifts, openid, 'gifts'),
                }
        else:
            if phone_num == user_gift.identity:
                has_gift = 'false'
            else:
                has_gift = 'true'
            self.debug_msg('openid:%s (phone:%s) 已经领取过奖品, gift:%s' %(openid, user_gift.identity, user_gift, ))
        gifts = self.get_distribute_status(order_id, activity)
        share_title, share_content, url = get_share_infos(order_id)
        return {
            "ret_code": 0,
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
<<<<<<< HEAD
            logger.debug("判断用户是否用此手机号在别的微信上领取过phone: %s, openid:%s, order_id:%s" %(phone_num, openid, order_id))
=======
            logger.debug("开奖页面，判断用户是否用此手机号在别的微信上领取过phone: %s, openid:%s, order_id:%s" %(phone_num, openid, order_id))
>>>>>>> cheche7/master
            award_user_gift = WanglibaoUserGift.objects.filter(rules__gift_id__exact=order_id, identity=str(phone_num), activity=self.activity).first()

            if not award_user_gift:  #用户这个手机号没有领取过，再判断这个微信号是否已经领取过
                user_gift = WanglibaoUserGift.objects.filter(rules__gift_id__exact=order_id, identity=str(openid), activity=self.activity).first()
                if not user_gift:
                    award_user_gift = None
                else:
                    award_user_gift = WanglibaoUserGift.objects.filter(rules__gift_id__exact=order_id, activity=self.activity).exclude(identity=(str(openid))).first()
<<<<<<< HEAD
                    logger.debug("已经从数据库里查到用户(%s)的领奖记录, openid:%s, order_id:%s" %(award_user_gift.identity, openid, order_id))
=======
                    logger.debug("开奖页面，已经从数据库里查到用户(%s)的领奖记录, openid:%s, order_id:%s" %(award_user_gift.identity, openid, order_id))
>>>>>>> cheche7/master
            return award_user_gift
        except Exception, reason:
            self.exception_msg(reason, u'判断用户领奖，数据库查询出错')
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
            gifts = WanglibaoUserGift.objects.filter(rules__gift_id__exact=order_id, valid=2).all()
            return gifts
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
        gifts = self.get_distribute_status(order_id)
        logger.debug("抵达End页面，order_id:%s, URL:%s" %(order_id, url))
        return {
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

        phone_number = phone.strip()
        redpack = WanglibaoUserGift.objects.filter(identity=phone, activity__code=attention_code).first()
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
