# encoding:utf-8
from django.conf import settings
if settings.ENV == settings.ENV_PRODUCTION:
    BIND_SUCCESS_TEMPLATE_ID = 'mxNfcoJ8lfpbL1gFdazCk1OFGBhm9wIGL21Q6ZeB5FI'
    UNBIND_SUCCESS_TEMPLATE_ID = "lGr-ClUgsv-ruam0ZvN_O-xy_7EzB__1tbCInUs_tOE"
    ACCOUNT_INFO_TEMPLATE_ID = 'EUnDdpMNocmYynxiw939HGwv0_uG1wDrvg-xJ-Lhdz8'
else:
    BIND_SUCCESS_TEMPLATE_ID = "8a21nArPQS0XWct6AGCASDqoaaaE_Ir5SaqarSqkNws"
    UNBIND_SUCCESS_TEMPLATE_ID = "BR08JlAXbQ_JUCnKWmhrSNe4pNL2PF9PQxV1QLcxrNo"
    ACCOUNT_INFO_TEMPLATE_ID = "EUnDdpMNocmYynxiw939HGwv0_uG1wDrvg-xJ-Lhdz8"
from copy import deepcopy

class MessageTemplate404(Exception):
    def __init__(self):
        pass

class MessageTemplate(object):
    def __init__(self, template_id, **kwargs):
        template = Message_template.get(template_id, {})
        if not template:
            raise MessageTemplate404
        self.template_id = template_id
        self.top_color = template.get('top_color')
        self.url = template.get('url', '')
        template_data = template.get("data", {})
        self.data = deepcopy(template_data)
        for key, value in kwargs.iteritems():
            if key in template_data:
                self.data[key]['value'] = kwargs.get(key)




Message_template = {
    "mxNfcoJ8lfpbL1gFdazCk1OFGBhm9wIGL21Q6ZeB5FI":{
        "top_color":'#88ffdd',
        "data": {
                "first": {
                    "value": u"账户绑定通知",
                   "color": "#173177"
                },
                "name1": {
                    "value": "",
                   "color": "#173177"
                },
                "name2": {
                    "value": "{value}",
                   "color": "#173177"
                },
                "time": {
                    "value": "{value}",
                   "color": "#173177"
                },
               "remark":{
                   "value":u'您可以使用下方微信菜单进行更多体验。',
                   "color":"#173177"
               }
        },
        "url": '',
    },

    "EUnDdpMNocmYynxiw939HGwv0_uG1wDrvg-xJ-Lhdz8":{
        "top_color":'#88ffdd',
        "data":{
                "first": {
                    "value": "账户概况",
                   "color": "#173177"
                },
                "keyword1": {
                    "value": "{value}",
                   "color": "#173177"
                },
                "keyword2": {
                    "value": "{value}",
                   "color": "#173177"
                },
                "keyword3": {
                    "value": "{value}",
                   "color": "#173177"
                },
                "keyword4": {
                    "value": "{value}",
                   "color": "#173177"
                },
               "remark":{
                   "value":u'账户详情',
                   "color":"#173177"
               }
        },
        "url": settings.CALLBACK_HOST + '/weixin/account/',
    },
    "BR08JlAXbQ_JUCnKWmhrSNe4pNL2PF9PQxV1QLcxrNo":{
        "first":{
            "value":u"尊敬的客户您好，您的账户已经解绑！",
            "color":"#173177"
        },
        "keyword1":{
            "value":"{value}",#解除账户：123456
            "color":"#173177"
        },
        "keyword2":{
            "value":"{value}",#解绑时间：2014年7月21日 18:36
            "color":"#173177"
        },
       "remark":{
           "value":u"如有疑问，请拨打6546544654",
           "color":"#173177"
       },
       "url":""
    }
}
