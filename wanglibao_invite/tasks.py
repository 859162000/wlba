# encoding: utf-8
from django.contrib.auth.models import User
from django.db import transaction
from wanglibao.celery import app
from weixin.models import WeixinUser
from .models import WechatUserDailyReward, InviteRelation
from utils import sendDailyReward

@app.task
def processShareInviteDailyReward(openid, user_id, new_registed=True):
    w_user = WeixinUser.objects.get(openid=openid)
    rewards = WechatUserDailyReward.objects.filter(w_user=w_user, status=False).all()
    user = User.objects.get(id=user_id)
    for reward in rewards:
        sendDailyReward(user, reward.id, openid, True, new_registed)





