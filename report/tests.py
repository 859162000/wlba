# coding=utf-8
from django.test import TestCase
from django.utils import timezone
from report.reports import DepositReportGenerator


class ReportGeneratorTestCase(TestCase):
    def test_deposit_report(self):
        from wanglibao_account.mock_generator import MockGenerator as UserMockGenerator
        UserMockGenerator.generate_user()

        from wanglibao_pay.mock_generator import PayMockGenerator
        PayMockGenerator.generate_bank()
        PayMockGenerator.generate_card()
        PayMockGenerator.generate_payinfo()

        report = DepositReportGenerator.generate_report(timezone.now() + timezone.timedelta(days=-1))
        self.assertTrue(report.name.startswith(u'充值'))
