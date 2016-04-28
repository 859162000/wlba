#!/usr/bin/env python
# encoding:utf-8
import logging
import time

import requests
from django.contrib.auth.models import User

from wanglibao import settings
from wanglibao.celery import app
from wanglibao_account.models import Message, MessageText, MessageNoticeSet, message_type
from BeautifulSoup import BeautifulSoup

logger = logging.getLogger('wanglibao_inside_messages')


def count_msg(params, user):
    """
        计算消息条数
    """
    logger.info('in count message!!!!!!')
    listtype = params.get("listtype", "").strip()
    if not listtype or listtype not in ("read", "unread", "all"):
        return {"ret_code": 30071, "message": "参数输入错误"}

    if settings.PHP_INSIDE_MESSAGE_SWITCH == 1:
        if listtype == "unread":
            count = Message.objects.filter(target_user=user, read_status=False, notice=True).count()
        elif listtype == "read":
            count = Message.objects.filter(target_user=user, read_status=True, notice=True).count()
        else:
            count = Message.objects.filter(target_user=user).count()
        return {"ret_code": 0, "message": "ok", "count": count}

    else:
        logger.info('in PHP_INSIDE_MESSAGE_SWITCH != 1')
        try:
            response = requests.post(settings.PHP_INSIDE_MESSAGES_LIST,
                                     data={'uid': user.id, 'read_status': listtype}, timeout=3)
            resp = response.json()
            if resp['code'] == 'success':
                count = len(resp['data'])
                return {"ret_code": 0, "message": "ok", "count": count}
            else:
                return {"ret_code": 10001, "message": "failed", "count": -1}
        except Exception, e:
            return {"ret_code": 10002, "message": e.message, "count": -1}


def list_msg(params, user):
    """
        分页获取消息
    """
    pagesize = params.get("pagesize", "10").strip()
    pagenum = params.get("pagenum", "").strip()
    listtype = params.get("listtype", "").strip()
    if not pagenum or not listtype:
        return {"ret_code": 30081, "message": "信息输入不完整"}
    if not pagenum.isdigit() or not pagesize.isdigit() or listtype not in ("read", "unread", "all"):
        return {"ret_code": 30082, "message": "参数输入错误"}
    pagenum = int(pagenum)
    pagesize = int(pagesize)
    if not 1 <= pagenum < 100 or not 1 <= pagesize <= 50:
        return {"ret_code": 30083, "message": "参数输入错误"}

    if settings.PHP_INSIDE_MESSAGE_SWITCH == 1:
        if listtype == "unread":
            msgs = Message.objects.filter(target_user=user, read_status=False, notice=True
                                          ).order_by('-message_text__created_at')[(pagenum-1)*pagesize:pagenum*pagesize]
        elif listtype == "read":
            msgs = Message.objects.filter(target_user=user, read_status=True, notice=True
                                          ).order_by('-message_text__created_at')[(pagenum-1)*pagesize:pagenum*pagesize]
        else:
            msgs = Message.objects.filter(target_user=user).order_by('-message_text__created_at')[(pagenum-1)*pagesize:pagenum*pagesize]

    else:
        response = requests.post(settings.PHP_INSIDE_MESSAGES_LIST,
                                 data={'uid': user.id, 'read_status': listtype}, timeout=3)
        resp = response.json()
        messages = []
        if resp['code'] == 'success':
            count = len(resp['data'])
            data = resp['data']
            messages = Message.objects.all()[:count]

            # 把 data 的数据 赋值都展示的messages 对象
            index = 0
            for message in messages:
                message.id = data[index]['id']
                message.read_status = True if data[index]['read_status'] == str(1) else False
                message.message_text.title = data[index]['title']
                message.message_text.content = data[index]['content']
                message.message_text.created_at = int(data[index]['created_at'])
                index += 1

        msgs = []
        msgs.extend(messages)

    rs = []
    mt = dict(message_type)
    dtype = {}
    for x in msgs:
        content = x.message_text.content
        obj = {"id": x.id, "title": x.message_text.title, "content": content,
               "mtype": mt[x.message_text.mtype],
               "created_at": time.strftime("%Y-%m-%d", time.localtime(x.message_text.created_at)),
               "read_status": x.read_status}
        rs.append(obj)
        bs = BeautifulSoup(content)
        arr = bs.findAll('a')
        for item in arr:
            if hasattr(item,'href') and item['href'] not in dtype:
                if item['href'] == "/":
                    dtype[item['href']] = 'index'
                    dtype[item.text] = 'index'
                elif item['href'].startswith("/pay/banks"):
                    dtype[item['href']] = 'pay'
                    dtype[item.text] = 'pay'
                elif item['href'].startswith("/accounts/home"):
                    dtype[item['href']] = 'home'
                    dtype[item.text] = 'home'
                elif item['href'].startswith("/accounts/id_verify"):
                    dtype[item['href']] = 'validate'
                    dtype[item.text] = 'validate'
                else:
                    dtype[item['href']] = item['href']
                    dtype[item.text] = item['href']
    return {"ret_code": 0, "message": "ok", "data": rs, "dtype": dtype}


def sign_read(user, message_id):
    """
        标记消息已读
    """
    if int(message_id) == 0:
        if settings.PHP_INSIDE_MESSAGE_SWITCH == 1:
            Message.objects.filter(target_user=user, read_status=False).update(read_status=True, read_at=long(time.time()))
        else:
            url = settings.PHP_INSIDE_MESSAGE_READ_ALL
            response = requests.post(url,
                                     data={'uid': user.id}, timeout=3)
            resp = response.json()
            if resp['code'] == 'success':
                return {"ret_code": 0, "message": "ok"}
            else:
                return {"ret_code": 10000, "message": "请求超时"}
    else:
        if settings.PHP_INSIDE_MESSAGE_SWITCH == 1:
            msg = Message.objects.filter(target_user=user).filter(pk=message_id).first()
            if msg and not msg.read_status:
                msg.read_status = True
                msg.read_at = long(time.time())
                msg.save()
            elif not msg:
                return {"ret_code": 30091, "message": "消息不存在"}
        else:
            url = settings.PHP_INSIDE_MESSAGE_READ
            response = requests.post(url,
                                     data={'uid': user.id, 'mid': message_id}, timeout=3)
            resp = response.json()
            if resp['code'] == 'success':
                return {"ret_code": 0, "message": "ok"}
            else:
                return {"ret_code": 10000, "message": "请求超时"}


def create(title, content, mtype):
    if not title or not content or not mtype:
        return False
    nt = dict(message_type).keys()
    if mtype not in nt:
        return False
    msgTxt = MessageText()
    msgTxt.title = title
    msgTxt.content = content
    msgTxt.created_at = long(time.time())
    msgTxt.mtype = mtype
    msgTxt.save()
    return msgTxt
    
def _send(target_user, msgTxt, push_type):
    msg = Message()
    msg.target_user = target_user
    msg.message_text = msgTxt
    # mset = MessageNoticeSet.objects.filter(user=target_user, mtype=msgTxt.mtype).first()
    notice = True
    # #不管有没有设置，默认都发推送
    # if mset or not mset:
    #     #notice = mset.notice
    #     devices = UserPushId.objects.filter(user=target_user)
    #     if devices:
    #         channel = bae_channel.BaeChannel()
    #         msg_key = "wanglibao_%s" % time.time()
    #         message = {"message":msgTxt.content, "user_id":target_user.id, "type":push_type}
    #         for d in devices:
    #             if d.device_type in ("ios", "iPhone", "iPad"):
    #                 #res, cont = channel.pushIosMessage(d.push_user_id, d.push_channel_id, message, msg_key)
    #                 pass
    #             elif d.device_type == "android":
    #                 res, cont = channel.pushAndroidMessage(d.push_user_id, d.push_channel_id, message, msg_key)

    msg.notice = notice
    msg.save()
    return True


def _send_batch(user_objs, msgTxt, push_type):
    # notice_list = MessageNoticeSet.objects.filter(user__in=user_objs, mtype=msgTxt.mtype)
    msg_list = list()
    for user_obj in user_objs:

        msg = Message()
        msg.target_user = user_objs[user_obj]
        msg.message_text = msgTxt

        msg.notice = True

        msg_list.append(msg)

    Message.objects.bulk_create(msg_list)

    # devices = UserPushId.objects.filter(user__in=user_objs)
    #
    # channel = bae_channel.BaeChannel()
    # msg_key = "wanglibao_%s" % time.time()
    # message = {"message": msgTxt.content, "type":push_type}
    #
    # for device in devices:
    #     # notice = True
    #     #不管有没有设置，默认都发推送
    #     message['user_id'] = device.user.id
    #
    #     if device.device_type in ("ios", "iPhone", "iPad"):
    #         res, cont = channel.pushIosMessage(device.push_user_id, device.push_channel_id, message, msg_key)
    #     elif device.device_type == "android":
    #         res, cont = channel.pushAndroidMessage(device.push_user_id, device.push_channel_id, message, msg_key)

    return True


def notice_set(params, user):
    """
        设置消息通知
    """
    notice_type = params.get("notice_type", "").strip()
    value = params.get("value", "").strip()
    nt = dict(message_type).keys()
    if notice_type not in nt or value not in ("true", "false"):
        return {"ret_code": 1, "message": "参数输入错误"}
    if value == "true":
        value = True
    else:
        value = False
    mns = MessageNoticeSet.objects.filter(user=user, mtype=notice_type).first()
    if mns:
        if mns.notice != value:
            mns.notice = value
            mns.save()
    else:
        mns.user = user
        mns.mtype = notice_type
        mns.notice = value
        mns.save()
    return {"ret_code": 0, "message": "设置成功"}


@app.task
def send_all(msgTxt_id):
    time.sleep(5)
    msgTxt = MessageText.objects.filter(pk=msgTxt_id).first()
    if not msgTxt:
        return False
    pagesize = 50
    start = 0
    while True:
        users = User.objects.all()[start*pagesize:(start+1)*pagesize]
        if not users:
            break
        for x in users:
            msg = Message()
            msg.target_user = x
            msg.message_text = msgTxt
            msg.read_status = False
            msg.read_at = 0
            msg.notice = True
            msg.save()
        start += 1
    return "send to all ok"


@app.task
def send_one(user_id, title, content, mtype, push_type="in"):
    """
        给某个人发送站内信（需要推送时也在这里写）
    """
    logger.info('going to send message ! user_id = {}'.format(user_id))
    if settings.PHP_INSIDE_MESSAGE_SWITCH == 1:
        msgTxt = create(title, content, mtype)
        if not msgTxt:
            return False

        user = User.objects.filter(pk=user_id).first()
        if not user:
            return False
        _send(user, msgTxt, push_type)
        return True
    elif settings.PHP_INSIDE_MESSAGE_SWITCH == 2:
        # 本地备份
        logger.info('inside message args, title = {}, content = {}, mtype = {}'.format(title, content, mtype))
        msgTxt = create(title, content, mtype)
        if not msgTxt:
            return False

        user = User.objects.filter(pk=user_id).first()
        if not user:
            return False
        _send(user, msgTxt, push_type)
        # PHP 发送
        try:
            response = requests.post(settings.PHP_SEND_INSIDE_MESSAGE,
                                     data={'uid': user_id, 'mtype': mtype, 'title': title, 'content': content},
                                     timeout=3)
            return response.json().get('status')
        except Exception, e:
            logger.debug('exception = {}'.format(e.message))
            logger.debug('failed info, uid = {}, mtype = {}, title = {}, content = {}'.format(
                user_id, mtype, title, content
            ))
            return False

    else:
        # PHP 发送
        try:
            response = requests.post(settings.PHP_SEND_INSIDE_MESSAGE,
                                     data={'uid': user_id, 'mtype': mtype, 'title': title, 'content': content},
                                     timeout=3)
            return response.json().get('status')
        except Exception, e:
            logger.debug('exception = {}'.format(e.message))
            logger.debug('failed info, uid = {}, mtype = {}, title = {}, content = {}'.format(
                user_id, mtype, title, content
            ))
            return False


@app.task
def send_batch(users, title=None, content=None, mtype=None, msgTxt=None, push_type="in"):
    """
        批量发送站内信, users is a user_id list.
    """
    logger.info('going to send message ! user_ids = {}'.format(users))
    if settings.PHP_INSIDE_MESSAGE_SWITCH == 1:
        if not isinstance(msgTxt, MessageText):
            msgTxt = create(title, content, mtype)
            if not msgTxt:
                return False

        user_objs = User.objects.in_bulk(users)
        _send_batch(user_objs, msgTxt, push_type)
        return True

    elif settings.PHP_INSIDE_MESSAGE_SWITCH == 2:
        if not isinstance(msgTxt, MessageText):
            msgTxt = create(title, content, mtype)
            if not msgTxt:
                return False

        user_objs = User.objects.in_bulk(users)
        _send_batch(user_objs, msgTxt, push_type)

        # PHP 发送
        try:
            response = requests.post(settings.PHP_SEND_INSIDE_MESSAGE,
                                     data={'uid': users, 'mtype': mtype, 'title': title, 'content': content}, timeout=30)
            return response.json().get('status')

        except Exception, e:
            logger.debug('exception = {}'.format(e.message))
            logger.debug('send batch failed info, uid = {}, mtype = {}, title = {}, content = {}'.format(
                users, mtype, title, content
            ))

            return False

    else:
        # PHP 发送
        try:
            response = requests.post(settings.PHP_SEND_INSIDE_MESSAGE,
                                     data={'uid': users, 'mtype': mtype, 'title': title, 'content': content}, timeout=3)
            return response.json().get('status')

        except Exception, e:
            logger.debug('exception = {}'.format(e.message))
            logger.debug('send batch failed info, uid = {}, mtype = {}, title = {}, content = {}'.format(
                users, mtype, title, content
            ))
            return False


def send_prepayment(user_records):
    '''
    msg_list = list()
    for user_record in user_records:

        msg = Message()
        msg.target_user = user_record.user

        msg.message_text = msgTxt

        msg.notice = True

        msg_list.append(msg)

    Message.objects.bulk_create(msg_list)

    devices = UserPushId.objects.filter(user__in=user_objs)

    channel = bae_channel.BaeChannel()
    msg_key = "wanglibao_%s" % time.time()
    message = {"message": msgTxt.content, "type":push_type}

    for device in devices:
        # notice = True
        #不管有没有设置，默认都发推送
        message['user_id'] = device.user.id

        if device.device_type in ("ios", "iPhone", "iPad"):
            res, cont = channel.pushIosMessage(device.push_user_id, device.push_channel_id, message, msg_key)
        elif device.device_type == "android":
            res, cont = channel.pushAndroidMessage(device.push_user_id, device.push_channel_id, message, msg_key)

    '''
    pass
    return True
