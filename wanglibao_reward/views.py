#-*- coding: utf-8 -*-
#########################################################################
# Author: Yihen Liu
# Created Time: 2015-09-09 13:23:07
# File Name: reward.py
# Description: 策划活动中的红包、奖品、加息券等用户奖励行为，独立在这个文件中
#########################################################################
from django.utils import timezone
from django.http.response import HttpResponse
from django.db.models import Count, Q
from datetime import datetime
from wanglibao_redpack.models import RedPackEvent
from wanglibao_redpack import backends as redpack_backends
import time
import json
import logging
logger = logging.getLogger('marketing')
from wanglibao_account import message as inside_message
from marketing.models import IntroducedBy, Reward
from wanglibao_reward.models import WanglibaoActivityGift, WanglibaoUserGift, WanglibaoActivityGiftGlobalCfg
from wanglibao_activity.models import Activity

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

    def __init__(self, request, activity):
        self.request = request
        self.activity = activity

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

        record = IntroducedBy.objects.filter(user_id=self.request.user.id).first()

        if not record:
            to_json_response = {
                'ret_code': 3001,
                'message': u'非渠道用户',
            }
        else:
            if record.channel.name not in channels:
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
        record = WanglibaoUserGift.objects.filter(activity=self.activity, name=name, Q(valid=0)|Q(valid=1)).aggregate(counts=Count("id"))
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
            rules=WanglibaoActivityGift.objects.filter(activity=self.activity, name=reward["name"]),
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

# vim: set noexpandtab ts=4 sts=4 sw=4 :

