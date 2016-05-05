# tencoding:utf-8

from django.test import SimpleTestCase
from wanglibao_pay.third_pay import query_trx
from wanglibao_pay.tasks import sync_pay_result
from datetime import datetime, timedelta
from mock import MagicMock
from django.utils.timezone import get_default_timezone
import logging

# tests without create db, command: 
# python manage.py test wanglibao_pay.no_create_db_tests --testrunner wanglibao.testrunner.NoCreateDBRunner

logger = logging.getLogger(__name__)

class QueryTrxTest(SimpleTestCase):
    def test_query_trx(self):
        pay_info_ids = (('# kuai fail', 1932529),
                ('# kuai success', 1934059),
                ('# kuai proceeding', 1931489),
                ('# kuai not exist', 1929872),
                ('# yeepay fail', 1934019),
                ('# yeepay success', 1934017),
                ('# yeepay proceeding', 1934015),
                ('# yeepay not exist', 1768494))

        for msg, pay_info_id  in pay_info_ids:
            try:
                res = query_trx(pay_info_id)
                print msg
                print res
            except:
                logger.exception('query_trx %s failed:'%(pay_info_id))

class TaskSyncPayResultTest(SimpleTestCase):

    def test_sync_pay_result(self):
        timezone = get_default_timezone()
        start_time = timezone.localize(datetime(2016,4,28))
        end_time = timezone.localize(datetime(2016, 4,29))
        sync_pay_result(start_time, end_time)

















