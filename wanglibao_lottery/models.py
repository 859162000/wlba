# encoding:utf-8
from django.contrib.auth.models import User

from django.db import models
from django.utils import timezone


class Lottery(models.Model):
    user = models.ForeignKey(User, related_name='lottery',null=False)
    buy_time = models.DateTimeField(help_text="彩票获赠时间", default=timezone.now)
    lottery_type = models.CharField(help_text="彩票类型", default="SSQ", max_length=50)
    money_type = models.FloatField(help_text="分彩类型", default=0.1)
    count = models.IntegerField(help_text="获赠注数", default =1, null=False)
    #出票后获得
    bet_number = models.CharField(help_text="投注号码", null=True, max_length=50)
    open_time = models.DateTimeField(help_text="开奖时间", null=True)
    issue_number = models.IntegerField(help_text="彩票期数", null=True)
    status = models.CharField(help_text="彩票状态",null=False, max_length=50)
    #开奖后获得
    win_number = models.CharField(help_text="中奖号码",null=True, max_length=50)
    prize = models.FloatField(help_text="中奖金额", null=True)