# encoding=utf-8
from django.utils.timezone import localtime

if __name__ == '__main__':
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wanglibao.settings')

from wanglibao_lottery.models import Lottery
from datetime import datetime

from django.test.testcases import TestCase
import requests
from wanglibao_account.auth_backends import User
from wanglibao_lottery.lotterytrade import LotteryTrade


def test_whole_process():
    user = User.objects.get(id=1)
    #order
    mlottery = LotteryTrade().order(user)
    assert mlottery.pk is not None
    print mlottery.pk, mlottery.buy_time
    #issue
    data = {
            'orderId':mlottery.id,
            'ballNo':'05,07,17,19,22,31,11',
            'issueNo':'2015091',
            #下列参数没有被后端使用，只是传递到后端做校验
            'status': '已出票',
            'gameId': 'SSQ',
            'moneyType': '0.1'
        }
    sign = LotteryTrade()._get_sign(data)
    data['sign'] = sign
    r = requests.get('http://127.0.0.1:8000/lottery/issue/', params=data)
    print r.url
    mlottery = Lottery.objects.get(pk=mlottery.pk)
    assert mlottery.bet_number == '05,07,17,19,22,31,11'
    print localtime(mlottery.open_time).date()
    assert localtime(mlottery.open_time).date() == datetime(2015, 8, 6).date()
    assert mlottery.issue_number == 2015091
    print 'status:%s,%s'%(mlottery.status, len(mlottery.status))
    assert mlottery.status == u'已出票'

    #open
    data = {
            'orderId':mlottery.id,
            'prizeNo':'05,07,17,19,22,31,11',
            'prizeMoneyAfterTax':'300.01',
            #下列参数没有被后端使用，只是传递到后端做校验
            'issueNo': '2015091',
            'gameId': 'SSQ',
            'rewardMoney': '500.01',
            'prizeMoney': '500.01',
            'prizeLevel': '1',
            'tax': '100.01',
        }
    sign = LotteryTrade()._get_sign(data)
    data['sign'] = sign
    r = requests.get('http://127.0.0.1:8000/lottery/open', params=data)
    print r.url
    #开奖后获得
    mlottery = Lottery.objects.get(pk=mlottery.pk)
    assert mlottery.win_number == u'05,07,17,19,22,31,11'
    assert mlottery.prize == 300.01
    assert mlottery.status == u'已中奖'
    #清理
    # mlottery.delete()
    
if __name__ == '__main__':
    test_whole_process()


