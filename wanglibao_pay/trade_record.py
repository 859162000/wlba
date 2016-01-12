#!/usr/bin/env python
# encoding:utf-8

# from django.utils import timezone
from wanglibao_pay.models import PayInfo
from wanglibao_pay import util
from wanglibao_p2p.models import UserAmortization, AmortizationRecord
# from wanglibao_margin.models import MarginRecord
from wanglibao_rest import utils as rest_utils


def detect(request):
    stype = request.DATA.get("type", "").strip()
    pagesize = request.DATA.get("pagesize", "10").strip()
    pagenum = request.DATA.get("pagenum", "1").strip()
    product_id = request.DATA.get("product_id", "").strip()
    device = rest_utils.split_ua(request)
    device_type = rest_utils.decide_device(device['device_type'])
    try:
        app_version = device['app_version']
    except KeyError:
        app_version = ''

    if not stype or stype not in ("deposit", "withdraw", "amortization"):
        return {"ret_code": 30191, "message": u"错误的类型"}
    if not pagesize.isdigit() or not pagenum.isdigit():
        return {"ret_code": 30192, "message": u"请输入正确的参数"}
    pagesize = int(pagesize)
    pagenum = int(pagenum)
    if pagesize > 100:
        return {"ret_code": 30193, "message": u"参数超出限制"}
    if product_id:
        if not product_id.isdigit():
            return {"ret_code": 30194, "message": u"产品号错误"}
        else:
            product_id = int(product_id)

    user = request.user
    if stype == "deposit":
        res = _deposit_record(user, pagesize, pagenum)
    elif stype == "withdraw":
        res = _withdraw_record(user, pagesize, pagenum, app_version)
    else:
        res = _amo_record(user, pagesize, pagenum, product_id)
    return {"ret_code": 0, "data": res, "pagenum": pagenum}


def _deposit_record(user, pagesize, pagenum):
    res = []
    records = PayInfo.objects.filter(user=user, type="D").exclude(status=PayInfo.PROCESSING)[(pagenum-1)*pagesize:pagenum*pagesize]
    for x in records:
        obj = {
            "id": x.id,
            "amount": x.amount,
            "created_at": util.fmt_dt_normal(util.local_datetime(x.create_time)),
            "status": x.status,
            "channel": "APP",
            "balance": x.margin_record.margin_current
        }
        if x.channel and x.channel == "huifu":
            obj['channel'] = "PC"
        res.append(obj)
    return res


def _withdraw_record(user, pagesize, pagenum, app_version):
    res = []
    records = PayInfo.objects.filter(user=user, type="W")[(pagenum-1)*pagesize:pagenum*pagesize]
    for x in records:
        if app_version and app_version < "2.6.3":
            fee = x.fee + x.management_fee
        else:
            fee = x.fee
        obj = {
            "id": x.id,
            "amount": x.total_amount,
            "created_at": util.fmt_dt_normal(util.local_datetime(x.create_time)),
            "status": x.status,
            "confirm_time": util.fmt_dt_normal(x.confirm_time),
            "card_no": x.card_no,
            "fee": fee,
            "management_fee": x.management_fee,
            "management_amount": x.management_amount,
            "channel": "APP"
        }
        if not x.channel:
            obj['channel'] = "PC"
        res.append(obj)
    return res


def _amo_record(user, pagesize, pagenum, product_id):
    res = []
    amos_record = AmortizationRecord.objects.select_related('amortization_product') \
        .filter(user=user).order_by('-created_time', '-id')
    if product_id:
        amos_record = amos_record.filter(amortization__product__id=product_id)
    amos_record = amos_record[(pagenum-1)*pagesize:pagenum*pagesize]
    for x in amos_record:
        obj = {
            "id": x.id,
            "name": x.amortization.product.name,
            "term": x.term,
            "total_term": x.amortization.product.amortization_count,
            "term_date": util.fmt_dt_normal(util.local_datetime(x.created_time)),
            "principal": x.principal,
            "interest": x.interest,
            "penal_interest": x.penal_interest,
            "coupon_interest": x.coupon_interest,
            "total_amount": (x.principal + x.interest + x.penal_interest + x.coupon_interest),
            "settlement_time": util.fmt_date_normal(util.local_datetime(x.created_time))
        }
        res.append(obj)
    return res
