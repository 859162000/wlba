#!/usr/bin/env python
# encoding:utf-8


from django.utils import timezone
from wanglibao_redpack.models import RedPack, RedPackRecord, RedPackEvent
from wanglibao_p2p.models import P2PRecord


def list_redpack(user, status):
    if status not in ("all", "expires", "unused", "used"):
        return {"ret_code":-1, "message":"参数错误"}

    if status == "unused":
        packages = {"unused":[]}
        records = RedPackRecord.objects.filter(user=user, redpack__status="unused")
        for x in records:
            obj = {"name":x.redpack_name, "receive_at":x.created_at,
                    "type":x.rule.rtype, "amount":x.rule.amount}
            if x.available_at < timezone.now() < x.unavailable_at:
                packages['unused'].append(obj)
    elif status == "used":
        packages = {"used":[]}
        records = RedPackRecord.objects.filter(user=user, redpack__status="used")
        for x in records:
            obj = {"name":x.redpack_name, "receive_at":x.created_at}
            if x.order_id:
                product = P2PRecord.objects.filter(order_id=x.order_id).values("product").first()
                packages['used'].append({"name":x.redpack_name, "product":product.name,
                                        "apply_at":x.apply_at, "receive_at":x.created_at,
                                        "apply_platform":x.apply_platform})
    elif status == "expires":
        packages = {"expires":[]}
        records = RedPackRecord.objects.filter(user=user, redpack__status="unused")
        for x in records:
            obj = {"name":x.redpack_name, "receive_at":x.created_at}
            if not x.order_id:
                if not x.available_at < timezone.now() < x.unavailable_at:
                    packages['expires'].append(obj)
    else:
        packages = {"used":[], "unused":[], "expires":[], "invalid":[]}
        records = RedPackRecord.objects.filter(user=user)
        for x in records:
            obj = {"name":x.redpack_name, "receive_at":x.created_at}
            if x.order_id:
                product = P2PRecord.objects.filter(order_id=x.order_id).values("product").first()
                packages['used'].append({"name":x.redpack_name, "product":product.name,
                                        "apply_at":x.apply_at, "receive_at":x.created_at,
                                        "apply_platform":x.apply_platform})
            else:
                if x.redpack.status == "invalid":
                    packages['invalid'].append(obj)
                elif x.redpack.status == "unused":
                    if not x.available_at < timezone.now() < x.unavailable_at:
                        packages['expires'].append(obj)
                    else:
                        packages['unused'].append(obj)
    return {"ret_code":0, "packages":packages}

def exchnage_redpack(token, device_type, user):
    if token == "":
        return {"ret_code":-1, "message":"请输入兑换码"}
    redpack = RedPack.objects.filter(token=token).first()
    if not redpack:
        return {"ret_code":-1, "message":"请输入正确的兑换码"}
    if redpack.status == "used":
        return {"ret_code":-1, "message":"兑换码已被兑换"}
    elif redpack.status == "invalid":
        return {"ret_code":-1, "message":"请输入有效的兑换码"}
    event = redpack.event
    if event.change_end_at < timezone.now():
        return {"ret_code":-1, "message":"请在%s之前兑换" % event.change_end_at}
    record = RedPackRecord()
    record.user = user
    record.redpack = redpack
    record.rule = event.rule
    record.redpack_name = event.name
    record.available_at = event.available_at
    record.unavailable_at = event.unavailable_at
    device_type = device_type.lower()
    if device_type == "ios":
        record.change_platform = "ios"
    elif device_type == "android":
        record.change_platform = "android"
    else:
        record.change_platform = "pc"
    redpack.status = "used"
    redpack.save()
    record.save()
    return {"ret_code":0, "message":"兑换成功"}
