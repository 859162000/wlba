#!/usr/bin/env python
# encoding:utf-8

import datetime
from marketing.utils import local_to_utc
from wanglibao_pay import util
from wanglibao_margin.models import MarginRecord


# 资金流水前后台字段对照表
MARGIN_CATALOG_MAPPING = {
    u"现金存入": u"充值",
    u"交易冻结": u"投资冻结",
    u"交易成功扣款": u"投资",
    u"交易解冻": u"投资失败退回",
    u"取款预冻结": u"提现申请",
    u"取款失败解冻": u"提现失败退回",
    u"取款确认": u"提现",
    u"返还手续费": u"手续费返还",
    u"本金入账": u"回款本金",
    u"利息入账": u"回款收益",
    u"加息存入": u"加息券收益",
    u"红包存入": u"红包存入",
    u"红包退回": u"红包退回",
    u"活动赠送": u"平台加息",
    u"体验金利息入账": u"体验金收益",
    u"全民淘金": u"佣金收益",
    u"体验金利息冲减": u"系统清算",
    u"活动收益冲减": u"系统清算",
}

# 资金流水前后台字段中资金增减对照表,
MARGIN_CATALOG_SIGN_MAPPING = {
    u"现金存入": u"+",
    u"交易冻结": u"-",
    u"交易成功扣款": u"",
    u"交易解冻": u"+",
    u"取款预冻结": u"-",
    u"取款失败解冻": u"+",
    u"取款确认": u"",
    u"返还手续费": u"+",
    u"本金入账": u"+",
    u"利息入账": u"+",
    u"加息存入": u"+",
    u"红包存入": u"+",
    u"红包退回": u"-",
    u"活动赠送": u"+",
    u"体验金利息入账": u"+",
    u"全民淘金": u"+",
    u"体验金利息冲减": u"-",
    u"活动收益冲减": u"-",
}


def margin_records(request):
    pagesize = request.DATA.get("pagesize", "10").strip()
    page = request.DATA.get("page", "1").strip()

    if not pagesize.isdigit() or not page.isdigit():
        return {"ret_code": 80001, "message": u"请输入正确的参数"}

    pagesize = int(pagesize)
    page = int(page)

    if pagesize > 100:
        return {"ret_code": 80002, "message": u"参数超出限制"}

    user = request.user

    # 展示的起始时间为2016年2月8日,此前有账单变动的用户由此时间开始展示,历史数据不展示
    date_start = local_to_utc(datetime.datetime(2016, 2, 8), 'min')
    records = MarginRecord.objects.filter(user=user, create_time__gt=date_start).order_by('-id')[(page-1)*pagesize:page*pagesize]

    res = []
    for record in records:
        obj = {
            "id": record.id,
            "catalog": MARGIN_CATALOG_MAPPING.get(record.catalog, record.catalog),
            "catalog_sign": MARGIN_CATALOG_SIGN_MAPPING.get(record.catalog, record.catalog),
            "create_time": util.fmt_dt_normal(util.local_datetime(record.create_time)),
            "amount": float(record.amount),
            "margin_current": float(record.margin_current),
            "description": record.description,
            "order_id": record.order_id
        }
        res.append(obj)
    return {"ret_code": 0, "data": res, "page": page}
