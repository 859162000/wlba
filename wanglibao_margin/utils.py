# coding=utf-8

import json
from django.contrib.auth.models import User
from .models import Margin
from .forms import MarginForm


def save_to_margin(req_data):
    margin = json.loads(req_data["margin"])
    sync_id = req_data["sync_id"]
    margin['sync_id'] = sync_id
    margin_instance = Margin.objects.filter(user_id=margin['user']).first()
    if margin_instance:
        if sync_id >= margin_instance.sync_id:
            margin_form = MarginForm(margin, instance=margin_instance)
            if margin_form.is_valid():
                margin_form.save()
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
                'ret_code': 10114,
                'message': u'小于当前margin的sync_id[%s]' % margin_instance.sync_id,
            }
    else:
        margin_form = MarginForm(margin)
        if margin_form.is_valid():
            user = User.objects.get(pk=margin['user'])
            margin['user'] = user
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

    return response_data
