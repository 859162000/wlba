#!/usr/bin/env python
# encoding:utf-8


import time
import random
import logging
from wanglibao.celery import app
from django.db import transaction
from wanglibao_redpack.models import RedPack, RedPackRecord, RedPackEvent
from misc.models import Misc
from django.conf import settings
from decimal import Decimal
import json

logger = logging.getLogger(__name__)

@app.task
def create_update_redpack(event_id):
    time.sleep(2)
    event = RedPackEvent.objects.filter(id=event_id).first()
    if not event:
        logger.debug("redpackevent %s not exists." % event_id)
        return
    rplist = RedPack.objects.filter(event=event)
    if not rplist.count():
        if event.value == 0:
            rp = RedPack()
            rp.event = event
            rp.status = "unused"
            rp.save()
            logger.debug("one redpack %s created." % rp.id)
        else:
            try:
                with transaction.atomic():
                    for x in range(event.value):
                        token = get_unused_token()
                        rp = RedPack()
                        rp.event = event
                        rp.token = token
                        #如果作废
                        if event.invalid:
                            rp.status = "invalid"
                        else:
                            rp.status = "unused"
                        rp.save()
            except:
                logger.debug("redpackevent %s to create list error." % event_id)
    else:
        if event.invalid:
            rplist.update(status="invalid")
        else:
            try:
                with transaction.atomic():
                    for x in rplist:
                        if x.status == "invalid":
                            x.status = "unused"
                            x.save()
            except:
                logger.debug("redpackevent %s to update list error." % event_id)
@app.task
def update_virtual_earning():
    key = 'virtual_incomes'
    rs = Misc.objects.filter(key=key).first()
    init_datas = [("133*****423",143203),("139*****254",138902),("138*****098",121001.4),
                          ("133*****409",109923),("137*****534",99407),("137*****341",84203.6),
                          ("186*****908",78002),("130*****691",73032),("139*****582",50367)]
    try:
        if rs:
            virtual_incomes = json.loads(rs.value)
            for virtual_income in virtual_incomes['virtual_incomes']:
                virtual_income[1] += random.randrange(100, 600)
            rs.value = json.dumps(virtual_incomes)
            rs.save()
        else:
            misc = Misc()
            misc.key = 'virtual_incomes'
            misc.value = json.dumps({key: init_datas})
            misc.description = "全民淘金排行虚拟数据"
            misc.save()
    except Exception, e:
        logger.debug("update_virtual_earning  error::%s" % e)

def get_unused_token():
    while True:
        token = rand_str()
        one = RedPack.objects.filter(token=token).first()
        #redpack = RedPack.objects.extra(where=["binary token='%s'" % token]).first()
        if not one:
            return token

def rand_str(num=10):
    return "".join(random.sample("ABCDEFGHJKLMNPQRSTUVWXY23456789ABCDEFGHJKLMNPQRSTUVWXY23456789ABCDEFGHJKLMNPQRSTUVWXY23456789ABCDEFGHJKLMNPQRSTUVWXY23456789ABCDEFGHJKLMNPQRSTUVWXY23456789abcdefghjkmnpqrstuvwxy23456789abcdefghjkmnpqrstuvwxy23456789abcdefghjkmnpqrstuvwxy23456789abcdefghjkmnpqrstuvwxy23456789abcdefghjkmnpqrstuvwxy23456789", num))
