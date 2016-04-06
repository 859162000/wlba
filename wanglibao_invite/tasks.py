# encoding: utf-8
from django.contrib.auth.models import User
from wanglibao.celery import app
from weixin.models import WeixinUser

@app.task
def processInviteReward(openid, user_id):
    user = User.objects.get(user_id)
    w_user = WeixinUser.objects.get(openid=openid)
    



