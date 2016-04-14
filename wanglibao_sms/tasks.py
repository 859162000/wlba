# -*- coding: utf-8 -*-
from wanglibao.celery import app
from .utils import send_messages as send_messages_impl
from wanglibao_sms.views import count_messages_arrived_rate, check_arrived_rate_tasks
from wanglibao_sms.send_php import PHPSendSMS


@app.task
def send_messages(phones, messages, channel=1, ext=''):
    return send_messages_impl(phones, messages, channel=channel, ext=ext)


@app.task
def send_sms_msg_one(rule_id, phone, content, user_type):
    """
    PHP发短信任务,直接发送短信文本内容
    单条短信发送
    :param rule_id:  rule id of php backend, default: 7
    :param phone:  phone number
    :param content:  sms content
    :param user_type: default value: phone
    """
    if not rule_id:
        rule_id = 7
    return PHPSendSMS().send_sms_msg_one(rule_id, phone, user_type, content)


@app.task
def send_sms_one(rule_id, phone, user_type, **kwargs):
    """
    PHP发短信任务,根据PHP后台模板中定义的参数名称和个数传递相应的参数,参数数量可变
    单条短信发送
    :param rule_id: rule id of php backend
    :param phone: phone number
    :param user_type: default value: phone
    """
    return PHPSendSMS().send_sms_one(rule_id, phone, user_type, **kwargs)


# 任务作废, 在纯脚本跑
@app.task
def message_arrived_rate_task():
    count_messages_arrived_rate()


# 任务作废, 在纯脚本跑
@app.task
def check_arrived_rate_task():
    check_arrived_rate_tasks()
