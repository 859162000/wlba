#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# Author: Yihen Liu
# Created Time: 2015-08-11 13:56:20
# File Name: anti.py
# Description: 反作弊定时任务
#########################################################################

import logging
from marketing import tools
from wanglibao_anti.models import AntiDelayCallback
from wanglibao_anti.anti.anti import GlobalParamsSpace
from wanglibao.celery import app
from json import JSONEncoder

logger = logging.getLogger(__name__)


@app.task
def handle_delay_time_data():
    """每过3分钟启动一次，处理星美等渠道的红包、积分情况,
        如果某个IP在过去的3分钟内，申请次数大于MAX_RECORD_FOR_ONE_IP
    """
    channels = GlobalParamsSpace.DELAY_CHANNELS
    max_record_for_one_ip = 20

    records = AntiDelayCallback.objects.filter(channel__in=channels, status=0).values("ip", "device", "uid")
    valid_records = dict()

    for record in records:
        valid_records[record['ip']].append(record)

    for record in [list().extend(item) for item in valid_records if len(item) <= max_record_for_one_ip]:
        device, uid = JSONEncoder.encoding(record["device"]), record["uid"]
        tools.register_ok.apply_async(kwargs={"user_id": id, "device": device})
        record.status = 1
        record.updatetime = int(time.time())
        record.save(update_fields=['status', 'updatetime'])
        logging.debug(" SUCCESS:%s, %s, %s" % (record.ip, record.uid, record.status))

    for record in [list().extend(item) for item in valid_records if len(item) > max_record_for_one_ip]:
        record.status = 2
        record.updatetime = int(time.time())
        record.save(update_fields=['status', 'updatetime'])
        logging.debug(" FAILED:%s, %s, %s" % (record.ip, record.uid, record.status))
