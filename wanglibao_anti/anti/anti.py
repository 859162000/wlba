#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# Author: Yihen Liu
# Created Time: 2015-08-11 13:56:20
# File Name: anti.py
# Description: 反作弊处理
#########################################################################
from json import *
import time
import logging
from wanglibao import settings
from wanglibao_anti.models import AntiDelayCallback
from marketing.utils import get_user_channel_record

logger = logging.getLogger('wanglibao_anti')


class GlobalParamsSpace(object):
    DELAY_CHANNELS = [u'365gu',]
    ANTI_DEBUG = True

class AntiBase(object):
    '''
        这是一个基类，定义了所有客户端都可能会用到的反作弊策略
    '''
    def __init__(self):
        pass

    def check_verified_code(self, request):
        '''
             校验码的检测，captcha_0:是一个hidden域，存储了从服务器端发送到web端的加密字符串
            captcha_1:存储了用户的输入结果
        '''

        captcha_0 = request.POST.get('captcha_0', "")
        captcha_1 = request.POST.get('captcha_1', "")

        if not captcha_0 or not captcha_1:
            return False
        else:
            return True

    def anti_run(self):
        pass


class AntiForAllClient(AntiBase):
    '''
        针对Web端特有的反作弊处理策略，都定义在这个类中
    '''
    def __init__(self, request):
        self.request = request

    def _write_to_hard_disk(self, channel):
        '''
            讲数据写文件，方便后期分析
            此处需要写入一个单独的anti log文件,方便问题的定位

        '''
        try:
            # TODO: open file but not close it, will make a big trouble ?
            handler = open("/var/log/wanglibao/anti_special_channel.log", "a")
            handler.write("%s\t%s\n" % (channel, time.strftime('%Y%m%d%H%M%S', time.gmtime())))
        except Exception, reason:
            logger.exception("_write_to_hard_disk Exception:%s" % (reason,))
        pass

    def anti_special_channel(self):
        '''
            针对特定渠道进行反作弊打击
        '''
        return True
        # comment by hb on 2015-12-16
        # invite_code = self.request.session.get(settings.PROMO_TOKEN_QUERY_STRING, '')
        # if invite_code in ("eleme", "xingmei"):
        #     self._write_to_hard_disk(invite_code)
        #     return self.check_verified_code(self.request)
        #
        # return True

    def anti_delay_callback_time(self, uid, device, where=None):
        '''
           针对特定的渠道，进行积分反馈延迟处理, 180s
        '''
        try:
            if where:
               channel = where
            else:
                # Modify by hb on 2015-12-16 : get user's channel from IntroducedBy
                #channel = self.request.session.get(settings.PROMO_TOKEN_QUERY_STRING, "")
                channel = get_user_channel_record(uid)
                if channel:
                    channel = channel.code
            if not channel:
                return False

            delay_channels = GlobalParamsSpace.DELAY_CHANNELS
            if channel in delay_channels:
                # Add by hb on 2015-12-16 : if can not get client_ip, then do nothing and renturn False
                try:
                    # Modify by hb on 2015-12-16 : for Nginx-Proxy, REMOTE_ADDR is unvalild, HTTP_X_REAL_IP may be work
                    #client_ip = self.request.META['HTTP_X_FORWARDED_FOR'] if self.request.META.get('HTTP_X_FORWARDED_FOR', None) else self.request.META.get('REMOTE_ADDR', "")
                    client_ip = self.request.META['HTTP_X_FORWARDED_FOR'] if self.request.META.get('HTTP_X_FORWARDED_FOR', None) else self.request.META.get('HTTP_X_REAL_IP', None)
                    if not client_ip:
                        raise Exception, u'client_ip is none'
                except Exception, ex:
                    logger.exception("=20151216= Failed to get client ip: [%s] [%s] [%s] [%s]" % (uid, device, channel, ex))
                    return False

                record = AntiDelayCallback()
                record.channel = channel
                record.device = JSONEncoder().encode(device)
                record.uid = uid
                record.createtime = int(time.time())
                record.status = 0
                record.updatetime = 0
                record.ip = client_ip
                record.save()

                logger.debug("=20151216= AntiDelay Success: [%s] [%s] [%s] [%s]" % (uid, device, channel, client_ip))

                return True
        except Exception, ex:
            logger.exception("=20151216= [%s]" % (ex))
            return False

    def anti_run(self):
        pass


class AntiForAndroidClient(AntiBase):
    '''
        针对Android App端特有的反作弊处理策略，都定义在这个类中
    '''
    def __init__(self):
        pass

    def anti_run(self):
        pass


class AntiForAppleClient(AntiBase):
    '''
        针对Apple App端特有的反作弊处理策略，都定义在这个类中
    '''
    def __init__(self):
        pass

    def anti_run(self):
        pass


class AntiForWebClient(AntiBase):
    '''
        针对Html5特有的反作弊处理策略，都定义在这个类中
    '''
    def __init__(self):
        pass

    def anti_run(self):
        pass


class AntiForHtml5Client(AntiBase):
    '''
        针对Html5特有的反作弊处理策略，都定义在这个类中
    '''
    def __init__(self):
        pass

    def anti_run(self):
        pass


class AntiForWeixinClient(AntiBase):
    '''
        针对Weixin特有的反作弊处理策略，都定义在这个类中
    '''
    def __init(self):
        pass

    def anti_run(self):
        pass


# vim: set noexpandtab ts=4 sts=4 sw=4 :
