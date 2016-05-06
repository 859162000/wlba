# encoding: utf-8

from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao.celery import  app
from datetime import datetime, timedelta
from django.utils.timezone import get_default_timezone
from wanglibao_pay.models import PayInfo
from wanglibao_pay.third_pay import query_trx
from wanglibao_pay.pay import PayOrder
from wanglibao_pay.exceptions import ThirdPayError
import logging
import smtplib
from wanglibao import settings
from email.parser import Parser
from decimal import Decimal
from celery.signals import worker_process_init
import Crypto

logger = logging.getLogger(__name__)

def send_mail(payinfo_id, user_name, user_phone, amount, message):
    # accountant_team_email = 'jiesuan@wanglibank.com'
    accountant_team_email = 'wangzhenhai@wanglibank.com'
    admin_email = 'guoya@wanglibank.com'
    from_addr = settings.SMTP_USER
    if settings.ENV == settings.ENV_PRODUCTION:
        env_notice = ''
    else:
        env_notice = '测试邮件'
    email_content = (
        'From: <%s>\n'
        'To: <%s>,<%s>\n'
        'Subject: 用户对账成功(%s)\n'
        '\n'
        '用户 %s 手机号 %s 支付订单 %s 成功，自动为其充值 %s 元\n'
        '第三方返回信息如下：\n'
        '%s\n'
    ) %(from_addr, accountant_team_email, admin_email,
          env_notice, user_name, user_phone, payinfo_id, amount, message)
    headers = Parser().parsestr(email_content)

    mail_server = smtplib.SMTP(settings.SMTP_SERVER, 25, 'localhost', 30)    
    mail_server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    mail_server.sendmail(headers['from'], headers['to'].split(','), email_content)
    import pdb;pdb.set_trace()
    mail_server.quit()

@app.task()
def sync_pay_result(start_time=None, end_time=None):
    """
    每十分钟去第三方更新当天的在5分钟之前开始且还在处理中的pay_info的处理结果
    并更新pay_info中相关记录的信息
    如果需要给用户打钱，还需要发邮件通知结算
    """

    # find pay_info
        # start of today
    if not (start_time and end_time):
        today = datetime.today()
        today_start = get_default_timezone().localize(datetime(today.year, today.month, today.day))
        five_min_before = get_default_timezone().localize(today - timedelta(minutes=5))
        start_time = today_start
        end_time = five_min_before
    # todo test performance
    # finished transaction
    # finished email
    # finished log
    pay_infos = PayInfo.objects.filter(type='D')\
                               .filter(channel__in=['kuaipay', 'yeepay_bind'])\
                               .filter(create_time__gte=start_time, create_time__lte=end_time)\
                               .filter(status='处理中', is_checked=False).all()

    pay_order = PayOrder()

    for pay_info in pay_infos:
        pay_result = query_trx(pay_info.order_id)

        code = pay_result['code']
        raw_response = pay_result['raw_response']
        amount = pay_result['amount']
        try:
            if isinstance(amount, str):
                amount = Decimal(amount).quantize(Decimal('.01'))
        except:
            amount = None
        last_card_no = pay_result['last_card_no']

        # found, succeed
        if code and int(code) == 0:
            # check 
            if amount != pay_info.amount or last_card_no != pay_info.card_no[-4:] :
                return

            pay_order.order_after_pay_succcess(amount, pay_info.order_id)
            profile = WanglibaoUserProfile.objects.get(user=pay_info.user)
            logger.critical('sync_pay_result_deposit for pay_info_id %s' % pay_info.id)
            send_mail(pay_info.id, profile.name, profile.phone, pay_info.amount, raw_response) 

@worker_process_init.connect
def crypto_init(**kwagrgs):
    Crypto.Random.atfork()
    

