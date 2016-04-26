# encoding:utf-8

from django.test import SimpleTestCase
from wanglibao_pay.third_pay import query_trx

# tests without create db, command: 
# python manage.py test wanglibao_pay.no_create_db_tests --testrunner wanglibao.testrunner.NoCreateDBRunner

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
            res = query_trx(pay_info_id)
            print msg
            print res


















