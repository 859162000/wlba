#!/usr/bin/env python
# encoding:utf-8

import logging
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from models import ExperienceAmortization
from marketing.utils import local_to_utc
from wanglibao.celery import app
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_sms import messages
from wanglibao_sms.tasks import send_messages
from wanglibao_account import message as inside_message

logger = logging.getLogger(__name__)


@app.task
def experience_repayment_plan():
    """
    体验标还款计划结算任务
    每天下午17:00分开始执行
    自动将当天17:00之间所有未结算的计划进行统一结算
    结算的利息自动计入用户的资金账户余额
    """
    print(u"Getting experience gold repayment plan to start!")
    now = datetime.now()
    # start = local_to_utc(datetime(now.year, now.month, now.day - 1, 17, 0, 0), 'normal')
    end = local_to_utc(datetime(now.year, now.month, now.day, 17, 0, 0), 'normal')

    with transaction.atomic():
        phone_list = list()
        message_list = list()
        amortizations = ExperienceAmortization.objects.filter(settled=False).filter(term_date__lt=end).select_for_update()
        for amo in amortizations:

            try:
                amo.settled = True
                amo.settlement_time = timezone.now()
                amo.save()

                if amo.interest > 0:
                    # 体验金利息计入用户账户余额
                    description = u"体验金利息入账:%s元" % amo.interest
                    user_margin_keeper = MarginKeeper(amo.user)
                    user_margin_keeper.deposit(amo.interest, description=description, catalog=u"体验金利息入账")

                # 发站内信
                if amo.interest > 6:
                    # 短信
                    phone_list.append(amo.user.wanglibaouserprofile.phone)
                    message_list.append(messages.experience_amortize(amo.user.wanglibaouserprofile.name, amo.interest))
                    # 站内信
                    title, content = messages.experience_amortize_msg(
                        amo.user.wanglibaouserprofile.name,
                        amo.product.name,
                        amo.product.period,
                        amo.settlement_time,
                        amo.interest
                    )
                    inside_message.send_one.apply_async(kwargs={
                        "user_id": amo.user.id,
                        "title": title,
                        "content": content,
                        "mtype": "amortize"
                    })

            except Exception, e:
                logger.error(u"experience repayment error, amortization id : %s , message: %s" % (amo.id, e.message))

        # 发短信
        send_messages.apply_async(kwargs={
            "phones": phone_list,
            "messages": message_list
        })
