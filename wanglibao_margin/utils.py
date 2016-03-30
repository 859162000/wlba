# coding=utf-8

import json
from .models import Margin
from .forms import MarginForm


def save_to_margin(req_data):
    margin = req_data.get("margin", '')
    if margin:
        margin = json.loads(margin)
        margin_instance = Margin.objects.filter(user_id=margin['user']).first()
        if margin_instance:
            margin_form = MarginForm(margin, instance=margin_instance)
        else:
            margin_form = MarginForm(margin)

        if margin_form.is_valid():
            if margin_instance:
                margin_form.save()
            else:
                margin_instance = Margin()
                for k, v in margin.iteritems():
                    setattr(margin_instance, k, v)
                margin_instance.save()

            response_data = {
                'ret_code': 10000,
                'message': 'success',
            }
        else:
            response_data = {
                'ret_code': 50003,
                'message': margin_form.errors.values()[0][0],
            }
    else:
        response_data = {
            'ret_code': 10112,
            'message': u'缺少margin参数',
        }

    return response_data
