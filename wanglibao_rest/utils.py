#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

def search(client, string):
    pattern = re.compile(client)
    return re.search(pattern, string)


def split_ua(request):
    if not request or "HTTP_USER_AGENT" not in request.META:
        return {"device_type":"pc"}
    ua = request.META['HTTP_USER_AGENT']
    arr = ua.split("/")
    if len(arr) < 5:
        return {"device_type":"pc"}
    dt = arr[1].lower()
    if "android" in dt:
        device_type = "android"
    elif "iphone" in dt or "ipad" in dt:
        device_type = "ios"
    else:
        device_type = "pc"
    return {"device_type":device_type, "app_version":arr[0],
            "channel_id":arr[2], "model":arr[1],
            "os_version":arr[3], "network":arr[4]}


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
