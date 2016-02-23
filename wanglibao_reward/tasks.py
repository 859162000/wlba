# -*- coding: utf-8 -*-
from wanglibao.celery import app
from utils import sendWechatPhoneRewardByRegister
from wanglibao_account.auth_backends import User

@app.task
def sendWechatPhoneReward(user_id):
    try:
        user = User.objects.get(id=user_id)
        sendWechatPhoneRewardByRegister(user)
    except:
        pass

