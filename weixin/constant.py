# encoding:utf-8
from django.conf import settings
if settings.ENV == settings.ENV_PRODUCTION:
    BIND_SUCCESS_TEMPLATE_ID = '8a21nArPQS0XWct6AGCASDqoaaaE_Ir5SaqarSqkNws'
    UNBIND_SUCCESS_TEMPLATE_ID = "BR08JlAXbQ_JUCnKWmhrSNe4pNL2PF9PQxV1QLcxrNo"
    ACCOUNT_INFO_TEMPLATE_ID = '3_BxoXsC9wnPQlYJ-Iq80-Ice5b1wIDMjKXzFzQUEeA'
    PRODUCT_ONLINE_TEMPLATE_ID = "itviF9BIU8BBjEXwPOEMiElLzFByxMZ6-FjvYapk8pY"
    AWARD_COUPON_TEMPLATE_ID  = "_-Xlr2icPtM5sXj0VKuF3fleKYR-Rl4a_h2gpcd_95M"
    WITH_DRAW_SUBMITTED_TEMPLATE_ID = "KUG_9_VDPdX78g8T2kshvZcE6GAZjxhK5nW2bvjmpJQ"#取现已受理通知
    WITH_DRAW_SUCCESS_TEMPLATE_ID = ""
    DEPOSIT_SUCCESS_TEMPLATE_ID = "EVvBX8AIlhih9E2YYdZYzMljF__JA-SrMSDTyUeNdcE"     #充值到账通知
    PRODUCT_AMORTIZATION_TEMPLATE_ID = "JlRMqfGNiPdeSjTrCR9w1OUgDEusr0e3YWwqyU89vQM"#项目还款通知
    PRODUCT_INVEST_SUCCESS_TEMPLATE_ID = "jcgCbkXDebiZPe0iNP4GWkH-SK4iM-gLWRdfRxzM9Ew"#投标成功通知
else:
    BIND_SUCCESS_TEMPLATE_ID = "v9Ol0oyYuaXK893W1pnMBAcncYu4a8TGKy4VQvsalJ4"
    UNBIND_SUCCESS_TEMPLATE_ID = "U9Py2H6uah6goLfNBsZREDkakU1iz6y_Qmxw1XgktXg"
    ACCOUNT_INFO_TEMPLATE_ID = "1mDbMYYEtpP1IJCEW-jwe-6yed_K3ug0TrOwkN5j2xo"
    PRODUCT_ONLINE_TEMPLATE_ID = "pzUuV-Oy08k-uGdFbR54GQpSn_HUbxHib1hwFS4vZSQ"
    AWARD_COUPON_TEMPLATE_ID  = ""
    WITH_DRAW_SUBMITTED_TEMPLATE_ID = "JLRdicikDz4IRO7uEmvnVoDAKsw7k95MEjU3rxP0Lmo"#取现已受理通知
    WITH_DRAW_SUCCESS_TEMPLATE_ID = ""
    DEPOSIT_SUCCESS_TEMPLATE_ID = "pp4ZxU9QdaAKUBvsR5z8JtGoNn3sYMliOH3HiaUUuGk"   #充值到账通知
    PRODUCT_AMORTIZATION_TEMPLATE_ID = "VogmmLb01RLW6RQrn3l4zpFpSh29pJw9Ki1YhnG4iPw"#项目还款通知
    PRODUCT_INVEST_SUCCESS_TEMPLATE_ID = "dHNrT8forqmVaGHZ3LCPIBPMU3jsnNXd6tykaWzQvRk"#投标成功通知

# else:#wangxiaoqing
#     BIND_SUCCESS_TEMPLATE_ID = "ze8Mgao5wi5SJpfkQB_OQUTiX9NqnB0V6oLsm_GaTFI"
#     UNBIND_SUCCESS_TEMPLATE_ID = "TtmpZytSck7cULmFw2Oo-LK2N2VZ5A4wQ1JpXmaoo2s"
#     ACCOUNT_INFO_TEMPLATE_ID = "RVeDKzQxeuxBXuWeZAjIyuv0olTh0HOWttFfqLhwDlU"
#     PRODUCT_ONLINE_TEMPLATE_ID = "CBIMqm2GrhDTlilYE_jLJkFxkzzOsDItSsRTDoKtO-Q"
#     AWARD_COUPON_TEMPLATE_ID  = ""
#     WITH_DRAW_SUBMITTED_TEMPLATE_ID = "pr2ECl9m81b57IwhW2O4_PmW5GeMMWpGyUg-DymwsYg"#取现已受理通知
#     WITH_DRAW_SUCCESS_TEMPLATE_ID = ""
#     DEPOSIT_SUCCESS_TEMPLATE_ID = "_T5Akr3kBKo4gr5joQQseKqCjmAbbkawEBeHS9P4AuU"   #充值到账通知
#     PRODUCT_AMORTIZATION_TEMPLATE_ID = "h9Fxr0BbHP20wfYJ5D44YUWHaSuURmDeqngeY7NIu8o"#项目还款通知
#     PRODUCT_INVEST_SUCCESS_TEMPLATE_ID = "wbV38-H2u0LkOZRGjB3fWMpj4CczgMdAP7aiTg4SM8A"#投标成功通知

# else:#hmm's
#     BIND_SUCCESS_TEMPLATE_ID = "mxNfcoJ8lfpbL1gFdazCk1OFGBhm9wIGL21Q6ZeB5FI"
#     UNBIND_SUCCESS_TEMPLATE_ID = "lGr-ClUgsv-ruam0ZvN_O-xy_7EzB__1tbCInUs_tOE"
#     ACCOUNT_INFO_TEMPLATE_ID = "M0xyqNNdrwtQl_901eJ13BJP9_BTK1pTk6NU9hmpGes"
#     PRODUCT_ONLINE_TEMPLATE_ID = "LQADSfNMmbZdTrz2UsRic93aPb_7cS1TUjUSx7tbxHE"
#     AWARD_COUPON_TEMPLATE_ID  = "_-Xlr2icPtM5sXj0VKuF3fleKYR-Rl4a_h2gpcd_95M"
#     WITH_DRAW_SUBMITTED_TEMPLATE_ID = "Paf_qr_WiojI3BddoDvqNKMI1C7KRzayEA_XGrmgQac"#取现已受理通知
#     WITH_DRAW_SUCCESS_TEMPLATE_ID = ""
#     DEPOSIT_SUCCESS_TEMPLATE_ID = "LuwpMH6CdEP2IeEsB7h6uewLhZdrnQPb0vmjDlqWh70"     #充值到账通知
#     PRODUCT_AMORTIZATION_TEMPLATE_ID = "wDHmjettSpgHys4HMXdcndUfkloiQNu2j9LXTa_qkO4"#项目还款通知
#     PRODUCT_INVEST_SUCCESS_TEMPLATE_ID = "JgSYj3TqABs9UbmA33QfkZ2ZGjHL436oBBvOMpyWGh8"#投标成功通知
# else:#玉姣's
#     BIND_SUCCESS_TEMPLATE_ID = "XFyiciGriKwniC2SFGwh476H5kjQcnVzRCinWQpuDU8"#绑定通知
#     UNBIND_SUCCESS_TEMPLATE_ID = "TjTDJSN5G02O0A6lBl16hDDMWa_QQ_W_msFiJJMB1hk"#解绑通知
#     ACCOUNT_INFO_TEMPLATE_ID = "uF7aZpQWUbvEXP8vVQRiXYRhLNOP73BdKAtb8IHyJTg"#账户信息通知
#     PRODUCT_ONLINE_TEMPLATE_ID = "ahEXfjXGTBuUfi5mhldgiCy5PyqAtCHqZLvfW6Mrx6U"#项目上线通知
#     AWARD_COUPON_TEMPLATE_ID  = ""#暂时不用
#     WITH_DRAW_SUBMITTED_TEMPLATE_ID = "CVVTdimar58smTZwzKc3tNbhljIGMB9AafDIFB2bBOQ"#取现已受理通知
#     WITH_DRAW_SUCCESS_TEMPLATE_ID = ""#暂时不用
#     DEPOSIT_SUCCESS_TEMPLATE_ID = "R3UNq2ZvB3JrwlKSlMeEBNlDPTDi_o5wuXXRQ2TCljI"     #充值到账通知
#     PRODUCT_AMORTIZATION_TEMPLATE_ID = "dQZJtqzbGnw06fLrTBkvTyMRynEgZ0J93UD1Rs6maJY"#项目还款通知
#     PRODUCT_INVEST_SUCCESS_TEMPLATE_ID = "5cPoYu4IHv68uiPkBOGljhTw2ctHRYcDRFTfRxYFhzA"#投标成功通知


from copy import deepcopy

class MessageTemplate404(Exception):
    def __init__(self):
        pass

class MessageTemplate(object):
    def __init__(self, template_id, **kwargs):
        print kwargs
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
    PRODUCT_INVEST_SUCCESS_TEMPLATE_ID:{
        "top_color":'#88ffdd',
        "data": {
# 您好，您已投标成功。
# 标的编号：10023
# 投标金额：￥3000.00
# 投标时间：2015-09-12
# 投标成功,可在投标记录里查看.
# {{first.DATA}} 标的编号：{{keyword1.DATA}} 投标金额：{{keyword2.DATA}} 投标时间：{{keyword3.DATA}} {{remark.DATA}}
                "first": {
                    "value": "您好，您已投标成功",
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
                   "value":"",
                   "color":"#173177"
               }
        },
        "url": '',
    },
    PRODUCT_AMORTIZATION_TEMPLATE_ID:{
        "top_color":'#88ffdd',
        "data": {
            # 您好，您投资的项目还款完成
            # 项目名称：宝马X5-HK20151112002
            # 还款金额：1000元
            # 还款时间：2015-11-12
            # 详情请登录平台会员中心查看
            # {{first.DATA}} 项目名称：{{keyword1.DATA}} 还款金额：{{keyword2.DATA}} 还款时间：{{keyword3.DATA}} {{remark.DATA}}
                "first": {
                    "value": "您好，您投资的项目还款完成",
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
                   "value":"",
                   "color":"#173177"
               }
        },
        "url": '',
    },
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
                   "value":"",
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
                    "value": u"绑定通知",
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
                   "color":"#000000"
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
        "url": settings.CALLBACK_HOST + '/weixin/account/?promo_token=fwh',
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
