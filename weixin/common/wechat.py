# encoding:utf-8
from __future__ import unicode_literals
from weixin.wechatpy import create_reply
import urllib
import requests

# 公众号类型
class WeixinAccounts(object):

    data = {
        'main': {
            'id': '',
            'name': '网利宝',
            'app_id': 'wx896485cecdb4111d',
            'app_secret': 'b1e152144e4a4974cd06b8716faa98e1',
            'classify': '已认证服务号'
        },
        'sub_1': {
            'id': 'gh_77c09ff2f3a3',
            'name': '网利宝',
            'app_id': 'wx110c1d06158c860b',
            'app_secret': '2523d084edca65b6633dae215967a23f',
            'classify': '已认证订阅号',
            'EncodingAESKey': '3QXabFsqXV64Bvdc4EvRciOfvWbYw7Fud38J8ianHmx'
        }
    }

    @classmethod
    def get(cls, key):
        return cls.data.get(key)


class Permission(object):
    """
    公众号权限验证
    微信支付接口  需申请 微信认证服务号支持
    微信小店接口  需申请 微信认证服务号支持
    微信卡券接口  需申请 微信认证订阅号和微信认证服务号支持
    微信设备功能接口    需申请 微信认证服务号支持
    """

    permission = {
        # 基础支持-获取access_token
        'access_token_api': ('0', '1', '2', '3'),
        # 基础支持-获取微信服务器IP地址
        'weixin_ip_api': ('0', '1', '2', '3'),
        # 接收消息-验证消息真实性、接收普通消息、接收事件推送、接收语音识别结果
        'reception_message_api': ('0', '1', '2', '3'),
        # 发送消息-被动回复消息
        'reply_message_api': ('0', '1', '2', '3'),
        # 发送消息-客服接口
        'kf_api': ('1', '3'),
        # 发送消息-群发接口
        'mass_api': ('1', '3'),
        # 发送消息-模板消息接口（发送业务通知）
        'template_api': ('3',),
        # 用户管理-用户分组管理
        'user_group_api': ('1', '3'),
        # 用户管理-设置用户备注名
        'user_remark_api': ('1', '3'),
        # 用户管理-获取用户基本信息
        'user_info_api': ('1', '3'),
        # 用户管理-获取用户列表
        'user_list_api': ('1', '3'),
        # 用户管理-获取用户地理位置
        'user_location_api': ('3',),
        # 用户管理-网页授权获取用户openid/用户基本信息
        'oauth_api': ('3',),
        # 推广支持-生成带参数二维码
        'qrcode_api': ('3',),
        # 推广支持-长链接转短链接口
        'short_url_api': ('3',),
        # 界面丰富-自定义菜单
        'menu_api': ('1', '2', '3'),
        # 素材管理-素材管理接口
        'media_api': ('1', '3'),
        # 智能接口-语义理解接口
        'semantic_api': ('3',),
        # 多客服-获取多客服消息记录、客服管理
        'customer_service_api': ('3',),
        # 微信JS-SDK-基础接口
        'js_sdk_base': ('0', '1', '2', '3'),
        # 微信JS-SDK-分享接口
        'js_sdk_share': ('1', '3'),
        # 微信JS-SDK-图像接口
        'js_sdk_image': ('0', '1', '2', '3'),
        # 微信JS-SDK-音频接口
        'js_sdk_audio': ('0', '1', '2', '3'),
        # 微信JS-SDK-智能接口（网页语音识别）
        'js_sdk_ai': ('0', '1', '2', '3'),
        # 微信JS-SDK-设备信息
        'js_sdk_network': ('0', '1', '2', '3'),
        # 微信JS-SDK-地理位置
        'js_sdk_location': ('0', '1', '2', '3'),
        # 微信JS-SDK-界面操作
        'js_sdk_interface': ('0', '1', '2', '3'),
        # 微信JS-SDK-微信扫一扫
        'js_sdk_qrcode': ('0', '1', '2', '3'),
        # 微信JS-SDK-微信小店
        'js_sdk_shop': ('3',),
        # 微信JS-SDK-微信卡券
        'js_sdk_card': ('1', '3',),
        # 微信JS-SDK-微信支付
        'js_sdk_pay': ('3',),
    }

    @classmethod
    def verify_api(cls, account, api_name):
        if account is None:
            return False
        return account.classify in cls.permission.get(api_name, [])


def gen_token(length=8):
    import random
    import string
    salt = ''.join(random.sample(string.ascii_letters + string.digits, length))
    return salt


def tuling(msg):
    query_params = {
        'key': '9d6abfaecc7102d7d9b22b51ed0efe80',
        'info': msg.content,
        'userid': msg.source
    }
    url = 'http://www.tuling123.com/openapi/api?%s' % urllib.urlencode(query_params)
    res = requests.get(url)
    reply = create_reply('呵呵', msg)

    if res.status_code == 200:
        data = res.json()
        if data.get('code') == 100000:
            reply = create_reply(data.get('text'), msg)

    return reply