# encoding=utf-8
from datetime import datetime, timedelta

from wanglibao.celery import app
from wanglibao_lottery.models import Lottery


@app.task
def lottery_set_status():
    """
    每天早上八点重置未中奖用户的状态
    :return:
    """
    utc_yesterday = (datetime.today() - timedelta(days=1))
    lotteries = Lottery.objects.filter(open_time__gte=utc_yesterday).fitler(status='已出票').all()
    for lottery in lotteries:
        lottery.status = '未中奖'
        lottery.save()


