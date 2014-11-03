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

def assem_params(login_type, request):
    if login_type == "xunlei":
        uri = "/platform?"
        params = {"client_id":partner[login_type]["client_id"],
                "grant_type":"code","wap":0,
                "redirect_uri":settings.CALLBACK_HOST+"/accounts/login/callback/",
                "state":login_type}
        return partner[login_type]['api'] + uri + urllib.urlencode(params)
    else:
        return settings.LOGIN_REDIRECT_URL

def login_back2(request):
    args = request.GET
    user = request.user

    ret = args.get("ret", "")
    code = args.get("code", "")
    state = args.get("state", "")
    if ret != "0" or not code or not state:
        return {"ret_code":30031, "message":"parameter error"}
    url = settings.CALLBACK_HOST+"/accounts/login/callback2/?ret=%s&code=%s&state=%s" % (ret, code, state)
    return {"ret_code":0, "message":"ok", "url":url}

def login_back(request):
    args = request.GET
    user = request.user
    location = "/accounts/home/?result="

    ret = args.get("ret", "")
    code = args.get("code", "")
    state = args.get("state", "")
    if ret != "0" or not code or not state:
        return {"ret_code":30031, "message":"parameter error", "url":location + "false"}

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
                return {"ret_code":30033, "message":"token error", "url":location + "false"}
            uri = "http://developer.open-api-auth.xunlei.com/get_user_info?"
            params = {"client_id":partner[state]['client_id'], "scope":"get_user_info", "access_token":dic['access_token']}
            url = uri + urllib.urlencode(params)
            response, content = http.request(url, 'GET')
            if str(response['status']) != "200":
                return {"ret_code":30034, "message":content, "url":location + "false"}
            userinfo = json.loads(content)

            """
            tmpuser = Binding.objects.filter(user=user).filter(btype=state).first()
            #绑定过的不再绑定,一对一关系
            if tmpuser and tmpuser.bid != userinfo['uid']:
                return {"ret_code":0, "message":"ok", "data":userinfo, "url":"/accounts/home/"}

            bindinfo = Binding.objects.filter(bid=userinfo['uid']).filter(btype=state).first()
            if bindinfo:
                if bindinfo.user != user:
                    return {"ret_code":0, "message":"ok", "data":userinfo, "url":"/accounts/home/"}
            else:
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
            if str(userinfo['isvip']) == "0":
                bindinfo.isvip = False
            else:
                bindinfo.isvip = True
            bindinfo.extra = '{"level":%s}' % userinfo['level']
            bindinfo.access_token = dic['access_token']
            bindinfo.refresh_token = dic['refresh_token']
            bindinfo.created_at = long(time.time())
            bindinfo.save()
            """

            rs = _bind_account(user, state, userinfo, dic)
            if rs:
                if str(userinfo['isvip']) == "0":
                    return {"ret_code":0, "isvip":0, "message":"ok", "data":userinfo, "url":location + "ok"}
                else:
                    return {"ret_code":0, "isvip":1, "message":"ok", "data":userinfo, "url":location + "vip"}
            else:
                return {"ret_code":30034, "message":"server error", "url":location + "false"}
        else:
            return {"ret_code":30033, "message":content, "url":location + "false"}
    else:
        return {"ret_code":30032, "message":"state error", "url":location + "false"}

#检查迅雷账号VIP
def check_xunlei(dic):
    state = "xunlei"
    uri = "http://developer.open-api-auth.xunlei.com/get_user_info?"
    params = {"client_id":partner[state]['client_id'], "scope":"get_user_info", "access_token":dic['access_token']}
    url = uri + urllib.urlencode(params)
    http = httplib2.Http()
    response, content = http.request(url, 'GET')
    if str(response['status']) != "200":
        return {"ret_code":30061, "message":content}

    userinfo = json.loads(content)
    if userinfo['result'] != 200:
        #刷新token
        uri_ref = "https://open-api-auth.xunlei.com/auth2/token?"
        params_ref = {"grant_type":"refresh_token", "refresh_token":dic['refresh_token'],
                    "client_id":partner["xunlei"]["client_id"], "client_secret":partner["xunlei"]["secret_key"]}
        url2 = uri_ref + urllib.urlencode(params_ref)
        response, content = http.request(url2, 'GET')
        if str(response['status']) != "200":
            return {"ret_code":30062, "message":content}
        dic = json.loads(content)
        if dic["result"] != 200:
            return {"ret_code":30063, "message":"token error"}

        #刷新完token,重新获取用户信息
        params['access_token'] = dic['access_token']
        url = uri + urllib.urlencode(params)
        response, content = http.request(url, 'GET')
        if str(response['status']) != "200":
            return {"ret_code":30064, "message":content}
        userinfo = json.loads(content)
        if userinfo['result'] != 200:
            return {"ret_code":30065, "message":content}

    rs = _bind_account(user, state, userinfo, dic)
    if rs:
        return {"ret_code":0, "message":"ok", "data":userinfo, "url":"/accounts/home/"}
    else:
        return {"ret_code":30066, "message":"server error"}

#内部方法，绑定和检查用户关系
def _bind_account(user, state, userinfo, dic):
    tmpuser = Binding.objects.filter(user=user).filter(btype=state).first()
    #绑定过的不再绑定,一对一关系
    if tmpuser and tmpuser.bid != userinfo['uid']:
        return True

    bindinfo = Binding.objects.filter(bid=userinfo['uid']).filter(btype=state).first()
    if bindinfo:
        if bindinfo.user != user:
            return True
    else:
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
    if str(userinfo['isvip']) == "0":
        bindinfo.isvip = False
    else:
        bindinfo.isvip = True
    bindinfo.extra = '{"level":%s}' % userinfo['level']
    bindinfo.access_token = dic['access_token']
    bindinfo.refresh_token = dic['refresh_token']
    bindinfo.created_at = long(time.time())
    bindinfo.save()
    return True
