# encoding=utf-8

from wanglibao_lottery.models import Lottery
import logging
from hashlib import md5
from datetime import timedelta
from django.contrib.auth.models import User
import requests
from wanglibao import settings
import wanglibao_profile
logger = logging.getLogger(__name__)

class LotteryTrade(object):
    def _get_sign(self, mdict):
        sorted_value_list = sorted([str(i) for i in mdict.values() if i is not None])
        text = '[' + ', '.join(sorted_value_list) + ']' +str(settings.LINGCAIBAO_KEY)
        m = md5()
        m.update(text)
        sign = m.hexdigest()
        return sign

    def _get_mobile_for_user(self, user):
        return wanglibao_profile.models.WanglibaoUserProfile.objects.get(user_id=user.id).phone

    def _request_order(self, lottery, user):
        """
        向零财宝请求下单
        :return:
        """
        request_data = dict(orderId=lottery.id,
                            mobile=self._get_mobile_for_user(user),
                            gameId=lottery.lottery_type,
                            moneyType=lottery.money_type,
                            channel=settings.LINGCAIBAO_CHANNEL_ID,)
        sign = self._get_sign(request_data)
        request_data['sign'] = sign
        result = requests.get(settings.LINGCAIBAO_URL_ORDER, params=request_data)
        if result.json()['result'] != '1':
            raise IOError('lottery order failed with para: %s with result: %s'%(request_data, result.json()))

    def order(self, user, money_type=0.1):
        """
        下单：尽力下单.失败不重试，不记录到数据库.无日志.
        :return:
        """
        lottery = Lottery.objects.create(user=user, money_type=money_type)
        try:
            self._request_order(lottery, user)
            lottery.status = "未出票"
            lottery.save()
            return lottery
        except :
            lottery.delete()
            raise

    def _get_open_time(self, issue_number):
        issue_delta = int(issue_number) - int(settings.LINGCAIBAO_BASE_ISSUE)
        i, j = divmod(issue_delta, 3)
        if j == 0:
            days_delta = 7 * i
        else:
            days_delta = 7 * i + 2 * j
        return settings.LINGCAIBAO_BASE_DATETIME + timedelta(days=days_delta)

    def issue(self, data, sign):
        """
        出票:设置bet_number, open_time, issue_number, status
        :return:
        """
        right_sign = self._get_sign(data)
        if right_sign != sign:
            raise ValueError('lottery sign error with para sign %s and right sign %s'%(sign, right_sign))

        lottery = Lottery.objects.get(id=data['lottery_id'])
        lottery.bet_number = data['bet_number']
        lottery.open_time = self._get_open_time(data['issue_number'])
        lottery.issue_number = data['issue_number']
        lottery.status = '已出票'
        lottery.save()
        return lottery


    def open(self, data, sign):
        """
        中奖: 设置win_number, prize
        :return:
        """
        right_sign = self._get_sign(data)
        if right_sign != sign:
            raise ValueError('lottery sign error with para sign %s and right sign %s'%(sign, right_sign))

        lottery = Lottery.objects.get(id=data['lottery_id'])
        lottery.win_number = data['win_number']
        lottery.prize = data['prize']
        lottery.status = '已中奖'
        lottery.save()
        return lottery
