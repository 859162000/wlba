#!/usr/bin/env python
# encoding:utf-8


import time
import random
import logging
from wanglibao.celery import app
from django.db import transaction
from wanglibao_redpack.models import RedPack, RedPackRecord, RedPackEvent
from django.conf import settings
from decimal import Decimal

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
def update_robot_earning():
    f = file(settings.BASE_DIR+'/wanglibao_redpack/data/topearnings.txt', 'r')
    lines = f.readlines()
    f.close()
    write_str = ""
    for line in lines:
        phone, amount_str = line.split(",")
        amount = Decimal(amount_str)
        amount += Decimal(random.randrange(100, 600))
        write_str += "%s,%s\n" % (phone, amount)
    f = file(settings.BASE_DIR + '/wanglibao_redpack/data/topearnings.txt', 'w')
    f.write(write_str)
    f.close()

def get_unused_token():
    while True:
        token = rand_str()
        one = RedPack.objects.filter(token=token).first()
        #redpack = RedPack.objects.extra(where=["binary token='%s'" % token]).first()
        if not one:
            return token

def rand_str(num=10):
    return "".join(random.sample("ABCDEFGHJKLMNPQRSTUVWXY23456789ABCDEFGHJKLMNPQRSTUVWXY23456789ABCDEFGHJKLMNPQRSTUVWXY23456789ABCDEFGHJKLMNPQRSTUVWXY23456789ABCDEFGHJKLMNPQRSTUVWXY23456789abcdefghjkmnpqrstuvwxy23456789abcdefghjkmnpqrstuvwxy23456789abcdefghjkmnpqrstuvwxy23456789abcdefghjkmnpqrstuvwxy23456789abcdefghjkmnpqrstuvwxy23456789", num))
