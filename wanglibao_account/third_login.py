#!/usr/bin/env python
# encoding:utf-8

import urllib
import json
import time
import httplib2
from django.conf import settings
from wanglibao_account.models import Binding

partner = {
    "xunlei":{"client_id":"dcaeeab92e5ef13b42127449fef99a24", 
            "secret_key":"ce202a0ecb73ef5e9aad1d8249979883",
            "api":"https://open-api-auth.xunlei.com"}
}

def assem_params(login_type):
    if login_type == "xunlei":
        uri = "/platform?"
        params = {"client_id":partner[login_type]["client_id"],
                "grant_type":"code","wap":0,
                "redirect_uri":settings.CALLBACK_HOST+"/accounts/login/callback/",
                "state":login_type}
        return partner[login_type]['api'] + uri + urllib.urlencode(params)
    else:
        return settings.LOGIN_REDIRECT_URL

def login_back(args, user):
    ret = args.get("ret", "")
    code = args.get("code", "")
    state = args.get("state", "")
    if ret != "0" or not code or not state:
        return {"ret_code":30031, "message":"parameter error"}

    if state == "xunlei":
        uri = "/auth2/token?"
        params = {"grant_type":"authorization_code", "code":code,
                "client_id":partner[state]["client_id"],
                "client_secret":partner[state]["secret_key"],
                "redirect_uri":settings.CALLBACK_HOST+"/accounts/login/callback/"}
        http = httplib2.Http()
        url = partner[state]['api'] + uri + urllib.urlencode(params)
        response, content = http.request(url, 'GET')
        if str(response['status']) == "200":
            dic = json.loads(content)
            if dic['result'] != 200:
                return {"ret_code":30033, "message":"token error"}
            uri = "http://developer.open-api-auth.xunlei.com/get_user_info?"
            params = {"client_id":partner[state]['client_id'], "scope":"get_user_info", "access_token":dic['access_token']}
            url = uri + urllib.urlencode(params)
            response, content = http.request(url, 'GET')
            if str(response['status']) != "200":
                return {"ret_code":30034, "message":content}
            userinfo = json.loads(content)

            tmpuser = Binding.objects.filter(user=user).filter(btype=state).first()
            #绑定过的不再绑定,一对一关系
            if tmpuser:
                return {"ret_code":0, "message":"ok", "data":userinfo, "url":"/accounts/home/"}
            tmpuser = Binding.objects.filter(bid=userinfo['uid']).filter(btype=state).first()
            if tmpuser:
                return {"ret_code":0, "message":"ok", "data":userinfo, "url":"/accounts/home/"}
            bindinfo = Binding()
            bindinfo.user = user
            bindinfo.btype = state
            bindinfo.bid = userinfo['uid']
            bindinfo.bname = userinfo['nickname']
            if userinfo['gender'] == "f":
                bindinfo.gender = "w"
            elif userinfo['gender'] == "m":
                bindinfo.gender = "m"
            else:
                bindinfo.gender = "n"
            bindinfo.access_token = dic['access_token']
            bindinfo.refresh_token = dic['refresh_token']
            bindinfo.created_at = long(time.time())
            bindinfo.save()
            return {"ret_code":0, "message":"ok", "data":userinfo, "url":"/accounts/home/"}
        else:
            return {"ret_code":30033, "message":content}
    else:
        return {"ret_code":30032, "message":"state error"}
