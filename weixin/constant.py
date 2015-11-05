# encoding:utf-8

BIND_SUCCESS_TEMPLATE_ID = '_8E2B4QZQC3yyvkubjpR6NYXtUXRB9Ya79MYmpVvQ1o'
ACCOUNT_INFO_TEMPLATE_ID = 'EUnDdpMNocmYynxiw939HGwv0_uG1wDrvg-xJ-Lhdz8'
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
    "_8E2B4QZQC3yyvkubjpR6NYXtUXRB9Ya79MYmpVvQ1o":{
        "top_color":'#88ffdd',
        "data": {
                "first": {
                    "value": "{value}",
                   "color": "#173177"
                },
                "keyword1": {
                    "value": "{value}",
                   "color": "#173177"
                },
        },
        "url": '',
    },
    "EUnDdpMNocmYynxiw939HGwv0_uG1wDrvg-xJ-Lhdz8":{
        "top_color":'#88ffdd',
        "data":{
                "first": {
                    "value": "{value}",
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
                   "value":"欢迎再次购买！",
                   "color":"#173177"
               }
        },
        "url": '',
    }
}
