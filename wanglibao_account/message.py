#!/usr/bin/env python
# encoding:utf-8


import time
from django.contrib.auth.models import User
from wanglibao.celery import app
from wanglibao_account.models import Message, MessageText, MessageNoticeSet, message_type

def count_msg(params, user):
    """
        计算消息条数
    """
    listtype = params.get("listtype", "").strip()
    if not listtype or listtype not in ("read", "unread", "all"):
        return {"ret_code":30071, "message":"参数输入错误"}
    if listtype == "unread":
        count = Message.objects.filter(target_user=user, read_status=False, notice=True).count()
    elif listtype == "read":
        count = Message.objects.filter(target_user=user, read_status=True, notice=True).count()
    else:
        count = Message.objects.filter(target_user=user).count()
    #actitype = "activity"
    #actcount = MessageText.objects.raw('select a.id from wanglibao_account_messagetext as a where a.id \
    #            not in (select message_text_id from wanglibao_account_message where user_id=%s) and a.mtype in (%s)' % (user.id, actitype)).count()
    return {"ret_code":0, "message":"ok", "count":count}

def list_msg(params, user):
    """
        分页获取消息
    """
    pagesize = 10
    pagenum = params.get("pagenum", "").strip()
    listtype = params.get("listtype", "").strip()
    if not pagenum or not listtype:
        return {"ret_code":30081, "message":"信息输入不完整"}
    if not pagenum.isdigit() or listtype not in ("read", "unread", "all"):
        return {"ret_code":30082, "message":"参数输入错误"}
    pagenum = int(pagenum)
    if not 1<=pagenum<100:
        return {"ret_code":30083, "message":"参数输入错误"}
    if listtype == "unread":
        msgs = Message.objects.filter(target_user=user, read_status=False, notice=True)[(pagenum-1)*pagesize:pagenum*pagesize]
    elif listtype == "read":
        msgs = Message.objects.filter(target_user=user, read_status=True, notice=True)[(pagenum-1)*pagesize:pagenum*pagesize]
    else:
        msgs = Message.objects.filter(target_user=user)[(pagenum-1)*pagesize:pagenum*pagesize]
    rs = []
    for x in msgs:
        rs.append({"id":x.id, "title":x.message_text.title, "content":x.message_text.content, 
                    "timestamp":x.message_text.created_at, "read_status":x.read_status})
    return {"ret_code":0, "message":"ok", "data":rs}

def sign_read(user, message_id):
    """
        标记消息已读
    """
    msg = Message.objects.filter(target_user=user).filter(pk=message_id).first()
    if msg and msg.read_status == False:
        msg.read_status = True
        msg.read_at = long(time.time())
        msg.save()
    elif not msg:
        return {"ret_code":30091, "message":"消息不存在"}
    return {"ret_code":0, "message":"ok"}

def create(title, content, mtype):
    if not title or not content or not mtype:
        return False
    msgTxt = MessageText()
    msgTxt.title = title
    msgTxt.content = content
    msgTxt.created_at = long(time.time())
    msgTxt.mtype = mtype
    msgTxt.save()
    return msgTxt
    
def send(target_user, msgTxt):
    msg = Message()
    if not isinstance(msgTxt, MessageText) or not isinstance(target_user, User):
        return False
    msg.target_user = target_user
    msg.message_text = msgTxt
    mset = MessageNoticeSet.objects.filter(user=target_user, mtype=msgTxt.mtype).first()
    notice = True
    if mset:
        notice = mset.notice
    msg.notice = notice
    msg.save()
    return True

def notice_set(params, user):
    """
        设置消息通知
    """
    notice_type = params.get("notice_type", "").strip()
    value = params.get("value", "").strip()
    nt = dict(message_type).keys()
    if notice_type not in nt or value not in ("true", "false"):
        return {"ret_code":1, "message":"参数输入错误"}
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
    return {"ret_code":0, "message":"设置成功"}


@app.task
def send_all(msgTxt_id):
    msgTxt = MessageText.objects.filter(pk=msgTxt_id).first()
    if not msgTxt:
        return False
    pagesize = 50
    start = 0
    return True
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
            msg.notice = notice
            msg.save()
        start += 1
    return "send to all ok"
