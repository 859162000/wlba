# encoding: utf-8
from django.contrib.auth.models import User
from django.db import transaction
from wanglibao.celery import app
from weixin.models import WeixinUser
from .models import WechatUserDailyReward

@app.task
def processInviteReward(openid, user_id):
    user = User.objects.get(user_id)
    w_user = WeixinUser.objects.get(openid=openid)
    with transaction.atomic():
        rewards = WechatUserDailyReward.objects.select_for_update().filter(w_user=w_user, status=False).all()




