# encoding: utf-8

from wanglibao.celery import  app
from datetime import datetime, timedelta
from django.utils.timezone import get_default_timezone
from wanglibao_pay.models import PayInfo
from wanglibao_pay.third_pay import query_trx
from wanglibao_pay.pay import PayOrder
from wanglibao_pay.exceptions import ThirdPayError
import logging

logger = logging.getLogger(__name__)

@app.task()
def sync_pay_result(start_time=None, end_time=None):
    """
    每十分钟去第三方更新当天的在5分钟之前开始且还在处理中的pay_info的处理结果
    并更新pay_info中相关记录的信息
    如果需要给用户打钱，还需要发邮件通知结算
    """
    accountant_team_email = 'jiesuan@wanglibank.com'
    admin_email = 'guoya@wanglibank.com'

    # find pay_info
        # start of today
    if not (start_time and end_time):
        today = datetime.today()
        today_start = get_default_timezone().localize(datetime(today.year, today.month, today.day))
        five_min_before = get_default_timezone().localize(today - timedelta(minutes=5))
        start_time = today_start
        end_time = five_min_before
    # todo test performance
    # todo transaction
    # todo email
    # todo log
    pay_infos = PayInfo.objects.filter(type='D')\
                               .filter(channel__in=['kuaipay', 'yeepay_bind'])\
                               .filter(create_time__gte=start_time, create_time__lte=end_time)\
                               .filter(status='处理中').all()

    pay_order = PayOrder()
    import pdb;pdb.set_trace()

    for pay_info in pay_infos:
        logger.debug('sync_pay_result for:%s'%pay_info.order_id)
        pay_result = query_trx(pay_info.order_id)

        code = pay_result['code']
        message = pay_result['message']
        amount = pay_result['amount']
        last_card_no = pay_result['last_card_no']

        # check 
        if amount != pay_info.amount or last_card_no != pay_info.card_no[-4:] != last_card_no:
            return

        try:
            if code == None:
                # None, not found
                raise ThirdPayError('20333', '用户未完成交易，第三方未找到交易信息')
            else:
                # found
                if int(code) == 0:
                    pay_order.order_after_pay_succcess(amount, pay_info.order_id)
                else:
                    raise ThirdPayError(code, message)
        except ThirdPayError, error:
            pay_order.order_after_pay_error(error, pay_info.order_id)



