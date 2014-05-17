# encoding: utf-8
import random
import datetime
from django.contrib.auth import get_user_model
from django.utils import timezone

from models import DailyIncome


class MockGenerator(object):
    @classmethod
    def generate_daily_income(cls, count=100, clean=False):
        if clean:
            [item.delete() for item in DailyIncome.objects.iterator()]

        users = get_user_model().objects.all()
        for u in users:
            for index in range(0, count):
                daily_income = DailyIncome()
                daily_income.date = timezone.datetime.today() + datetime.timedelta(days=-index)
                daily_income.user = u
                daily_income.income = random.randrange(0, 10000) / 100

                try:
                    daily_income.save()
                except:
                    continue
