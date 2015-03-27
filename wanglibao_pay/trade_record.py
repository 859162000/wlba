#!/usr/bin/env python
# encoding:utf-8


from django.utils import timezone
from wanglibao_pay.models import PayInfo
from wanglibao_pay import util
from wanglibao_p2p.models import UserAmortization
from wanglibao_margin.models import MarginRecord

def detect(request):
    stype = request.DATA.get("type", "").strip()
    pagesize = request.DATA.get("pagesize", "10").strip()
    pagenum = request.DATA.get("pagenum", "1").strip()

    if not stype or stype not in ("deposit", "withdraw", "amortization"):
        return {"ret_code":30191, "message":"错误的类型"}
    if not pagesize.isdigit() or not pagenum.isdigit():
        return {"ret_code":30192, "message":"请输入正确的参数"}
    pagesize = int(pagesize)
    pagenum = int(pagenum)
    if pagesize > 100:
        return {"ret_code":30193, "message":"参数超出限制"}

    user = request.user
    if stype == "deposit":
        res = _deposit_record(user, pagesize, pagenum)
    elif stype == "withdraw":
        res = _withdraw_record(user, pagesize, pagenum)
    else:
        res = _amo_record(user, pagesize, pagenum)
    return {"ret_code":0, "data":res, "pagenum":pagenum}

def _deposit_record(user, pagesize, pagenum):
    res = []
    #records = PayInfo.objects.filter(user=user, type="D", status=u"成功")[(pagenum-1)*pagesize:pagenum*pagesize]
    records = MarginRecord.objects.filter(user=user, catalog=u"现金存入")[(pagenum-1)*pagesize:pagenum*pagesize]
    for x in records:
        obj = {"id":x.id,
                "amount":x.amount, 
                "balance":x.margin_current,
                "created_at":util.fmt_dt_normal(util.local_datetime(x.create_time)),
                "channel":"APP"}
        channel = PayInfo.objects.filter(order=x.order_id).first()
        if channel and channel.channel == "huifu":
            obj['channel'] = "PC"
        res.append(obj)
    return res

def _withdraw_record(user, pagesize, pagenum):
    res = []
    #records = PayInfo.objects.filter(user=user, type="W", status=u"成功")[(pagenum-1)*pagesize:pagenum*pagesize]
    records = PayInfo.objects.filter(user=user, type="W")[(pagenum-1)*pagesize:pagenum*pagesize]
    for x in records:
        obj = {"id":x.id,
                "amount":x.amount, 
                "created_at":util.fmt_dt_normal(util.local_datetime(x.create_time)),
                "status":x.status,
                "confirm_time":util.fmt_dt_normal(x.confirm_time),
                "card_no":x.card_no,
                "channel":"APP"}
        if not x.channel:
            obj['channel'] = "PC"
        res.append(obj)
    return res

def _amo_record(user, pagesize, pagenum):
    res = []
    amos = UserAmortization.objects.filter(user=user, settled=True)[(pagenum-1)*pagesize:pagenum*pagesize]
    for x in amos:
        obj = {"id":x.id,
                "name":x.product_amortization.product.name, "term":x.term,
                "term_date":util.fmt_dt_normal(util.local_datetime(x.term_date)),
                "principal":x.principal, "interest":x.interest,
                "penal_interest":x.penal_interest,
                "total_amount":(x.principal+x.interest+x.penal_interest),
                "settlement_time":util.fmt_dt_normal(util.local_datetime(x.settlement_time))}
        res.append(obj)
    return res
