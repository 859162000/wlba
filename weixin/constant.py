# encoding:utf-8
from django.conf import settings
if settings.ENV == settings.ENV_PRODUCTION:
    BIND_SUCCESS_TEMPLATE_ID = '8a21nArPQS0XWct6AGCASDqoaaaE_Ir5SaqarSqkNws'
    UNBIND_SUCCESS_TEMPLATE_ID = "BR08JlAXbQ_JUCnKWmhrSNe4pNL2PF9PQxV1QLcxrNo"
    ACCOUNT_INFO_TEMPLATE_ID = '3_BxoXsC9wnPQlYJ-Iq80-Ice5b1wIDMjKXzFzQUEeA'
    PRODUCT_ONLINE_TEMPLATE_ID = "itviF9BIU8BBjEXwPOEMiElLzFByxMZ6-FjvYapk8pY"
    AWARD_COUPON_TEMPLATE_ID  = "_-Xlr2icPtM5sXj0VKuF3fleKYR-Rl4a_h2gpcd_95M"
    WITH_DRAW_SUBMITTED_TEMPLATE_ID = "KUG_9_VDPdX78g8T2kshvZcE6GAZjxhK5nW2bvjmpJQ"
    WITH_DRAW_SUCCESS_TEMPLATE_ID = ""
    DEPOSIT_SUCCESS_TEMPLATE_ID = "EVvBX8AIlhih9E2YYdZYzMljF__JA-SrMSDTyUeNdcE"
else:
    BIND_SUCCESS_TEMPLATE_ID = "mxNfcoJ8lfpbL1gFdazCk1OFGBhm9wIGL21Q6ZeB5FI"
    UNBIND_SUCCESS_TEMPLATE_ID = "lGr-ClUgsv-ruam0ZvN_O-xy_7EzB__1tbCInUs_tOE"
    ACCOUNT_INFO_TEMPLATE_ID = "RVeDKzQxeuxBXuWeZAjIyuv0olTh0HOWttFfqLhwDlU"
    PRODUCT_ONLINE_TEMPLATE_ID = "LQADSfNMmbZdTrz2UsRic93aPb_7cS1TUjUSx7tbxHE"
    AWARD_COUPON_TEMPLATE_ID  = "_-Xlr2icPtM5sXj0VKuF3fleKYR-Rl4a_h2gpcd_95M"
    WITH_DRAW_SUBMITTED_TEMPLATE_ID = "Paf_qr_WiojI3BddoDvqNKMI1C7KRzayEA_XGrmgQac"
    WITH_DRAW_SUCCESS_TEMPLATE_ID = ""
    DEPOSIT_SUCCESS_TEMPLATE_ID = "LuwpMH6CdEP2IeEsB7h6uewLhZdrnQPb0vmjDlqWh70"

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
        self.url = kwargs.get('url', template.get('url', ''))
        template_data = template.get("data", {})
        self.data = deepcopy(template_data)
        for key, value in kwargs.iteritems():
            if key in template_data:
                self.data[key]['value'] = kwargs.get(key)
        print self.data



Message_template = {
    DEPOSIT_SUCCESS_TEMPLATE_ID:{
        "top_color":'#88ffdd',
        "data": {
            # {{first.DATA}} 充值时间：{{keyword1.DATA}} 充值金额：{{keyword2.DATA}} 可用余额：{{keyword3.DATA}} {{remark.DATA}}
                "first": {
                    "value": "",
                   "color": "#173177"
                },
                "keyword1": {
                    "value": "",
                    "color": "#173177"
                },
                "keyword2": {
                    "value": "",
                    "color": "#173177"
                },
                "keyword3": {
                    "value": "",
                    "color": "#173177"
                },
               "remark":{
                   "value":u'您可以使用下方微信菜单进行更多体验。',
                   "color":"#173177"
               }
        },
        "url": '',
    },

    WITH_DRAW_SUCCESS_TEMPLATE_ID:{
        "top_color":'#88ffdd',
        "data": {
                "first": {
                    "value": "",
                   "color": "#173177"
                },

               "remark":{
                   "value":u'您可以使用下方微信菜单进行更多体验。',
                   "color":"#173177"
               }
        },
        "url": '',
    },

    WITH_DRAW_SUBMITTED_TEMPLATE_ID:{
        "top_color":'#88ffdd',
        "data": {
            # 亲爱的{}，您的提现申请已受理，1-3个工作日内将处理完毕，请耐心等待。
            # {{first.DATA}} 取现金额：{{keyword1.DATA}} 到账银行：{{keyword2.DATA}} 预计到账时间：{{keyword3.DATA}} {{remark.DATA}}
                "first": {
                    "value": "",
                   "color": "#173177"
                },
                "keyword1": {
                    "value": "",
                    "color": "#173177"
                },
                "keyword2": {
                    "value": "",
                    "color": "#173177"
                },
                "keyword3": {
                    "value": "",
                    "color": "#173177"
                },
               "remark":{
                   "value":u'您可以使用下方微信菜单进行更多体验。',
                   "color":"#173177"
               }
        },
        "url": '',
    },

    BIND_SUCCESS_TEMPLATE_ID:{
        "top_color":'#88ffdd',
        "data": {
                "first": {
                    "value": "",
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

    ACCOUNT_INFO_TEMPLATE_ID:{
        "top_color":'#88ffdd',
        "data":{
                "first": {
                    "value": "",
                   "color": "#173177"
                },
                "keyword1": {
                    "value": "{value}",#截止时间
                   "color": "#173177"
                },
                "keyword2": {
                    "value": "{value}",#  累计收益
                   "color": "#000000"
                },
               "remark":{
                   "value":u'',
                   "color":"#173177"
               }
        },
        "url": settings.CALLBACK_HOST + '/weixin/account/',
    },
    UNBIND_SUCCESS_TEMPLATE_ID:{
        "top_color":'#88ffdd',
        "data":{
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
               "value":u"",
               "color":"#173177"
           },
        },
       "url":""
    },
    PRODUCT_ONLINE_TEMPLATE_ID:{
        # {{first.DATA}} 项目名称：{{keyword1.DATA}} 年化收益率：{{keyword2.DATA}} 项目期限：{{keyword3.DATA}} 还款方式：{{keyword4.DATA}} {{remark.DATA}}
        "top_color":'#88ffdd',
        "data":{
                "first": {
                    "value": "{value}",#
                   "color": "#173177"
                },
                "keyword1": {
                    "value": "{value}",#项目名称
                   "color": "#173177"
                },
                "keyword2": {
                    "value": "{value}",#年化收益率
                   "color": "#173177"
                },
                "keyword3": {
                    "value": "{value}",#项目期限
                   "color": "#173177"
                },
                "keyword4": {
                    "value": "{value}",#还款方式
                   "color": "#173177"
                },
               "remark":{
                   "value":u'',
                   "color":"#173177"
               }
        },
        "url": "",
    },
    AWARD_COUPON_TEMPLATE_ID:{
        "top_color":'#88ffdd',
        "data":{
            "first":{
                "value":'{value}',
                "color":"#173177"
            },
            "present_income":{
                "value":"{value}",#获赠金额
                "color":"#173177"
            },
           "remark":{
               "value":u"如有疑问，请拨打6546544654",
               "color":"#173177"
           },
        },
       "url":""
    }
}
