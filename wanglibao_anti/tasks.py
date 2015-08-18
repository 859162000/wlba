#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# Author: Yihen Liu
# Created Time: 2015-08-11 13:56:20
# File Name: anti.py
# Description: 反作弊定时任务
#########################################################################

import logging
import time
from marketing import tools
from wanglibao_anti.models import AntiDelayCallback
from wanglibao_anti.anti.anti import GlobalParamsSpace
from wanglibao.celery import app
from json import JSONDecoder

logger = logging.getLogger('wanglibao_anti')


def recover_anti_user_data():
    """每过3分钟启动一次，处理星美等渠道的红包、积分情况,
        针对被误打的用户，人工手动干预标记为3，在下次任务启动的时候，重新向用户发送红包积分等
    """
    channels = GlobalParamsSpace.DELAY_CHANNELS
    records = AntiDelayCallback.objects.filter(channel__in=channels, status=3).values("updatetime", "status", "ip", "device", "uid")
    for record in records:
        device, uid = JSONDecoder().decode(record["device"]), record["uid"]
        tools.register_ok.apply_async(kwargs={"user_id": uid, "device": device})
        record.status = 1
        record.updatetime = int(time.time())
        record.save(update_fields=['status', 'updatetime'])
        logging.debug(" RECOVER:%s, %s, %s" % (record.ip, record.uid, record.status))


@app.task
def handle_delay_time_data():
    """每过3分钟启动一次，处理星美等渠道的红包、积分情况,
        如果某个IP在过去的3分钟内，申请次数大于max_record_for_one_ip,认为是作弊
    """

    recover_anti_user_data()

    channels = GlobalParamsSpace.DELAY_CHANNELS
    max_record_for_one_ip = 20

    records = AntiDelayCallback.objects.filter(channel__in=channels, status=0).values("updatetime","status", "ip", "device", "uid")
    valid_records = dict()

    for record in records:
        if record['ip'] not in valid_records.keys():
            valid_records[record['ip']] = list()
        valid_records[record['ip']].append(record)

    valid_list, invalid_list = list(), list()

    #处理正常用户
    [valid_list.extend(value) for value in valid_records.values() if len(value) <= max_record_for_one_ip ]
    for record in valid_list:
        device, uid = JSONDecoder().decode(record["device"]), record["uid"]
        tools.register_ok.apply_async(kwargs={"user_id": uid, "device": device})
        record.status = 1
        record.updatetime = int(time.time())
        record.save(update_fields=['status', 'updatetime'])
        logging.debug(" SUCCESS:%s, %s, %s" % (record.ip, record.uid, record.status))


    #处理疑似作弊的用户, 直接标记为2，并且不会有活动行为发生
    [ invalid_list.extend(value) for value in valid_records.values() if len(value) > max_record_for_one_ip ]
    for record in invalid_list:
        record.status = 2
        record.updatetime = int(time.time())
        record.save(update_fields=['status', 'updatetime'])
        logging.debug(" FAILED:%s, %s, %s" % (record.ip, record.uid, record.status))
