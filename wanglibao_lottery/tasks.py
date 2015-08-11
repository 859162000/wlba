# encoding=utf-8
from datetime import datetime, timedelta
from django.utils.timezone import get_default_timezone
from wanglibao.celery import app
from wanglibao_account.auth_backends import User
from wanglibao_lottery.lotterytrade import LotteryTrade
from wanglibao_lottery.models import Lottery
from wanglibao_p2p.models import P2PEquity


@app.task
def lottery_set_status():
    """
    每天早上八点重置未中奖用户的状态
    :return:
    """
    d = datetime.today()
    yesterday = get_default_timezone().localize(datetime(d.year, d.month, d.day))
    lotteries = Lottery.objects.filter(open_time__gte=yesterday).fitler(status='已出票').all()
    for lottery in lotteries:
        lottery.status = '未中奖'
        lottery.save()

@app.task
def send_lottery(user_id):
    #彩票规则：针对未投资的用户，首次投资1000元及以上，送1注彩票
    try:
        user = User.objects.get(id=user_id)
        equity = P2PEquity.objects.filter(user=user).get()
        if equity.equity >= 1000:
            LotteryTrade().order(user, money_type=1)
    except:
        pass



