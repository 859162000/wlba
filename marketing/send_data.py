#!/usr/bin/env python
# encoding:utf-8
from celery.utils.log import get_task_logger
from wanglibao.celery import app
from django.contrib.auth.models import User
from marketing.models import IntroducedBy,Channels
from marketing.utils import get_user_channel_record
from wanglibao_pay.models import PayInfo
from django.conf import settings
from django.utils import timezone
import requests
import json
import datetime
import logging
#logger = get_task_logger(__name__)
logger = logging.getLogger('marketing')

def sendData(message,param):
    """往数据部门提供的接口发送实时数据"""
    posturl = settings.SEND_PHP_URL
    #print json.dumps(message)
    try:
        res = requests.post(url = posturl, json=json.dumps(message))
        if res.status_code != 200:
            logger.info('response code error %s: %s:%s' % (res.status_code, param, str(message),))
        result = json.loads(res.text)
        if result['code'] != 0:
            logger.info('response text error %s: %s:%s' % (res.text, param, str(message),))
    except:
        logger.info('request server exception: %s:%s' % (param, str(message),))
    

@app.task
def send_register_data(user_id, device_type):
    """发送注册信息数据"""
    message = {}
    user = User.objects.filter(id=user_id).first()
    introduce = IntroducedBy.objects.filter(user=user).first()
    channel = get_user_channel_record(user_id)
    message['user_id'] = user.id
    message['zc_client'] = device_type
    #tel = user.wanglibaouserprofile.phone
    #message['tel'] = tel.replace(tel[3:-2], '*'*6)
    message['tel'] = user.wanglibaouserprofile.phone
    message['zc_time'] = timezone.localtime(user.date_joined).strftime('%Y-%m-%d %H:%M:%S')
    message['zc_from_userid'] = introduce.id if introduce else 0
    message['channel_id'] = channel.id if channel else 0
    message['channel_code'] = channel.code if channel else ''
    message['channel_image'] = channel.image.name if channel else ''
    message['channel_name'] = channel.name if channel else ''
    message['channel_description'] = channel.description if channel else ''
    message['channel_created_at'] = timezone.localtime(channel.created_at).strftime('%Y-%m-%d %H:%M:%S') if channel else ''
    data = {'act':1}
    data['data'] = message
    sendData(data,'register')

@app.task
def send_idvalidate_data(user_id, device_type):
    """发送实名信息数据"""
    message = {}
    user = User.objects.filter(id=user_id).first()
    message['user_id'] = user.id
    message['sm_client'] = device_type
    id_number = user.wanglibaouserprofile.id_number
    #身份证号18位的只传前4位和最后4位，身份证号15位的只传前4位和最后3位
    if len(id_number) == 18:
        message['id_number'] = id_number.replace(id_number[4:-4], '*'*10)
    else:
        message['id_number'] = id_number.replace(id_number[4:-3], '*'*8)
    message['sm_time'] = timezone.localtime(user.wanglibaouserprofile.id_valid_time).strftime('%Y-%m-%d %H:%M:%S')
    data = {'act':2}
    data['data'] = message
    sendData(data,'idvalidate')
    
@app.task
def send_deposit_data(user_id, amount, device_type, order_id):
    """发送充值信息数据"""
    message = {}
    user = User.objects.filter(id=user_id).first()
    message['user_id'] = user.id
    message['client'] = device_type
    pay_info = PayInfo.objects.filter(order_id=order_id).first()
    message['order_id'] = order_id
    message['amount'] = amount
    message['bank_name'] = pay_info.bank.name
    card_no = pay_info.card_no if pay_info.card_no else '0'
    if len(card_no)>1:
        message['card_num'] = card_no.replace(card_no[4:-3], '*' * len(card_no[4:-3]))
    message['time'] = timezone.localtime(pay_info.create_time).strftime('%Y-%m-%d %H:%M:%S')
    data = {'act':4}
    data['data'] = message
    sendData(data,'deposit')
    
@app.task
def send_investment_data(user_id, amount, device_type, order_id, product_id):
    """发送投资信息数据"""
    message = {}
    user = User.objects.filter(id=user_id).first()
    message['user_id'] = user.id
    message['client'] = device_type
    message['order_id'] = order_id
    message['amount'] = amount
    message['product_id'] = product_id
    message['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {'act':5}
    data['data'] = message
    sendData(data,'investment')
    
@app.task
def send_withdraw_data(user_id, amount, order_id, device_type):
    """发送提现信息数据"""
    message = {}
    user = User.objects.filter(id=user_id).first()
    message['user_id'] = user.id
    message['client'] = device_type
    pay_info = PayInfo.objects.filter(order_id=order_id).first()
    message['order_id'] = order_id
    message['amount'] = amount
    card_no = pay_info.card_no if pay_info.card_no else '0'
    if len(card_no)>1:
        message['card_num'] = card_no.replace(card_no[4:-3], '*' * len(card_no[4:-3]))
    message['time'] = timezone.localtime(pay_info.create_time).strftime('%Y-%m-%d %H:%M:%S')
    data = {'act':6}
    data['data'] = message
    sendData(data,'withdraw')