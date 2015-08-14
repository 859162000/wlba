#!/usr/bin/env python
# -*- coding: utf-8 -*-
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.http import HttpResponse

try:
    import json
except ImportError:
    from django.utils import simplejson as json

def captcha_refresh(request):
    """ 这个方法是从captcha第三库中改写过来的，用来响应非ajax请求的验证图片 """
    new_key = CaptchaStore.generate_key()
    to_json_response = {
        'key': new_key,
        'image_url': captcha_image_url(new_key),
    }
    return HttpResponse(json.dumps(to_json_response), content_type='application/json')
