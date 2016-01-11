# -*- coding: utf-8 -*-
from wanglibao.celery import app
from .utils import send_messages as send_messages_impl
from wanglibao_sms.views import count_messages_arrived_rate, check_arrived_rate_tasks


@app.task
def send_messages(phones, messages, channel=1, ext=''):
    return send_messages_impl(phones, messages, channel=channel, ext=ext)


# 任务作废, 在纯脚本跑
@app.task
def message_arrived_rate_task():
    count_messages_arrived_rate()


# 任务作废, 在纯脚本跑
@app.task
def check_arrived_rate_task():
    check_arrived_rate_tasks()
