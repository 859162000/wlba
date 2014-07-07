# encoding: utf-8
from decimal import Decimal
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from models import Margin, MarginRecord
from marginkeeper import MarginKeeper
from exceptions import MarginLack
# Create your tests here.


class MarginKeeperTestCase(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create(username='lowid')
        self.margin_keeper = MarginKeeper(self.user)

    def testSignal(self):
        user_margin = Margin.objects.get(user=self.user)
        self.assertEqual(user_margin.margin, Decimal('0'))

    def testDeposit(self):
        self.assertRaises(ValueError, self.margin_keeper.deposit, -100)
        self.assertRaises(ValueError, self.margin_keeper.deposit, 0)
        self.margin_keeper.deposit(100000)
        # test deposit result
        user_margin = Margin.objects.get(user=self.user)
        self.assertEqual(user_margin.margin, Decimal('100000.00'))
        self.assertEqual(user_margin.withdrawing, Decimal('0.00'))
        self.assertEqual(user_margin.freeze, Decimal('0.00'))
        # test deposit records
        margin_record = MarginRecord.objects.filter(catalog=u'现金存入').first()
        self.assertEqual(margin_record.amount, Decimal('100000.00'))
        self.assertEqual(margin_record.margin_current, Decimal('100000.00'))
        self.assertEqual(margin_record.user, self.user)

    def testFreeze(self):
        self.margin_keeper.deposit(100000, u'为测试冻结前预存款')
        self.margin_keeper.freeze(20000)
        self.margin_keeper.freeze(30000)
        user_margin = Margin.objects.get(user=self.user)
        self.assertEqual(user_margin.margin, 50000)
        self.assertEqual(user_margin.freeze, 50000)
        self.assertRaises(MarginLack, self.margin_keeper.freeze, 50001)
        # test freeze records
        margin_records = MarginRecord.objects.filter(catalog=u'交易冻结')
        self.assertEqual(margin_records.count(), 2)
        # test record order
        latest_margin_record = margin_records.first()
        self.assertEqual(latest_margin_record.amount, 30000)
        self.assertEqual(latest_margin_record.margin_current, 50000)
        self.assertEqual(latest_margin_record.user, self.user)

    def testUnfreeze(self):
        self.margin_keeper.deposit(100000, u'为测试冻结前预存款')
        self.margin_keeper.freeze(49571, u'申购冻结')
        self.assertRaises(MarginLack, self.margin_keeper.unfreeze, 50000)
        self.margin_keeper.unfreeze(49571, u'申购失败解冻')
        user_margin = Margin.objects.get(user=self.user)
        self.assertEqual(user_margin.freeze, 0)
        self.assertEqual(user_margin.margin, 100000)
        # test unfreeze records
        margin_records = MarginRecord.objects.filter(catalog=u'交易解冻')
        margin_record = margin_records.first()
        self.assertEqual(margin_record.user, self.user)
        self.assertEqual(margin_record.amount, 49571)
        self.assertEqual(margin_record.margin_current, 100000)

    def testSettle(self):
        self.margin_keeper.deposit(100000, u'为测试冻结前预存款')
        self.margin_keeper.freeze(49571, u'申购冻结')
        self.assertRaises(MarginLack, self.margin_keeper.settle, 59572)
        self.margin_keeper.settle(49571)
        user_margin = Margin.objects.get(user=self.user)
        self.assertEqual(user_margin.margin, 50429)
        self.assertEqual(user_margin.freeze, 0)
        self.assertEqual(user_margin.withdrawing, 0)
        # test settle records
        margin_records = MarginRecord.objects.filter(catalog=u'交易成功扣款')
        margin_record = margin_records.first()
        self.assertEqual(margin_record.user, self.user)
        self.assertEqual(margin_record.amount, 49571)
        self.assertEqual(margin_record.margin_current, 50429)

    def testWithdraw(self):
        self.margin_keeper.deposit(100000, u'为测试冻结前预存款')
        # test pre-freeze
        self.margin_keeper.withdraw_pre_freeze(10001)
        self.assertRaises(MarginLack, self.margin_keeper.withdraw_pre_freeze, 90000)
        self.assertRaises(ValueError, self.margin_keeper.withdraw_pre_freeze, 0)
        self.assertRaises(ValueError, self.margin_keeper.withdraw_pre_freeze, -1)
        user_margin = Margin.objects.get(user=self.user)
        self.assertEqual(user_margin.margin, 89999)
        self.assertEqual(user_margin.freeze, 0)
        self.assertEqual(user_margin.withdrawing, 10001)
        self.margin_keeper.withdraw_pre_freeze(9999)
        self.margin_keeper.withdraw_pre_freeze(1000)
        # test pre-freeze records
        margin_records = MarginRecord.objects.filter(catalog=u'取款预冻结')
        self.assertEqual(margin_records.count(), 3)
        latest_margin_record = margin_records.first()
        self.assertEqual(latest_margin_record.margin_current, 79000)
        self.assertEqual(latest_margin_record.amount, 1000)

        # until now, user margin should be:
        #   margin -> 79000.00
        #   withdrawing -> 21000.00
        #   freeze -> 0.00
        #   three withdraw in processing
        #   (10001, 9999, 1000)

        # test ack
        self.margin_keeper.withdraw_ack(1000)
        user_margin = Margin.objects.get(user=self.user)
        self.assertEqual(user_margin.margin, 79000)
        self.assertEqual(user_margin.withdrawing, 20000)
        # test ack records
        margin_records = MarginRecord.objects.filter(catalog=u'取款确认')
        margin_record = margin_records.first()
        self.assertEqual(margin_record.amount, 1000)
        self.assertEqual(margin_records.count(), 1)
        self.assertEqual(margin_record.user, self.user)
        self.assertEqual(margin_record.margin_current, 79000)

        # until now, user margin should be:
        #   margin -> 79000.00
        #   withdrawing -> 20000.00
        #   freeze -> 0.00
        #   two withdraw in processing
        #   (10001, 9999)

        # test rollback
        self.margin_keeper.withdraw_rollback(10001)
        user_margin = Margin.objects.get(user=self.user)
        self.assertEqual(user_margin.margin, 89001)
        self.assertEqual(user_margin.withdrawing, 9999)
        self.assertEqual(user_margin.freeze, 0)
        # test rollback with is_already_successful parm
        self.margin_keeper.withdraw_rollback(1000, is_already_successful=True)
        user_margin = Margin.objects.get(user=self.user)
        self.assertEqual(user_margin.withdrawing, 9999)
        self.assertEqual(user_margin.margin, 90001)
        self.assertEqual(user_margin.freeze, 0)
        # test rollback records
        margin_normal_rollback_records = MarginRecord.objects.filter(catalog=u'取款失败解冻')
        margin_normal_rollback_record = margin_normal_rollback_records.first()
        self.assertEqual(margin_normal_rollback_records.count(), 1)
        self.assertEqual(margin_normal_rollback_record.amount, 10001)
        self.assertEqual(margin_normal_rollback_record.margin_current, 89001)
        margin_is_already_successful_rollback_records = MarginRecord.objects.filter(catalog=u'取款渠道失败解冻')
        margin_is_already_successful_rollback_record = margin_is_already_successful_rollback_records.first()
        self.assertEqual(margin_is_already_successful_rollback_records.count(), 1)
        self.assertEqual(margin_is_already_successful_rollback_record.amount, 1000)
        self.assertEqual(margin_is_already_successful_rollback_record.margin_current, 90001)

        # until now, user margin should be:
        #   margin -> 90001.00
        #   withdrawing -> 9999.00
        #   freeze -> 0.00
        #   one withdraw in processing
        #   (9999, )

    def testAmortize(self):
        # test amortization without penal interest
        self.assertRaises(ValueError, self.margin_keeper.amortize, -10, 10, 20)
        self.assertRaises(ValueError, self.margin_keeper.amortize, 1, 0, 10)
        self.assertRaises(ValueError, self.margin_keeper.amortize, 1, 1 , -1)
        self.margin_keeper.amortize(1000, 100, 0)
        user_margin = Margin.objects.get(user=self.user)
        self.assertEqual(user_margin.margin, 1100)
        self.assertEqual(user_margin.freeze, 0)
        self.assertEqual(user_margin.withdrawing, 0)
        # test amortization with penal interest
        self.margin_keeper.amortize(2000, 200, 50)
        user_margin = Margin.objects.get(user=self.user)
        self.assertEqual(user_margin.margin, 3350)
        # test amortize records
        margin_principal_records = MarginRecord.objects.filter(catalog=u'还款入账', description=u'本金入账')
        margin_interest_records = MarginRecord.objects.filter(catalog=u'还款入账', description=u'利息入账')
        margin_penal_interest_records = MarginRecord.objects.filter(catalog=u'还款入账', description=u'罚息入账')
        margin_amortize_records = MarginRecord.objects.filter(catalog=u'还款入账')
        self.assertEqual(margin_principal_records.count(), 2)
        self.assertEqual(margin_interest_records.count(), 2)
        self.assertEqual(margin_penal_interest_records.count(), 1)
        self.assertEqual(margin_amortize_records.count(), 5)

        self.assertEqual(margin_principal_records[0].user, self.user)
        self.assertEqual(margin_principal_records[0].amount, 2000)
        self.assertEqual(margin_principal_records[0].margin_current, 3100)
        self.assertEqual(margin_principal_records[1].user, self.user)
        self.assertEqual(margin_principal_records[1].amount, 1000)
        self.assertEqual(margin_principal_records[1].margin_current, 1000)

        self.assertEqual(margin_interest_records[0].user, self.user)
        self.assertEqual(margin_interest_records[0].amount, 200)
        self.assertEqual(margin_interest_records[0].margin_current, 3300)
        self.assertEqual(margin_interest_records[1].user, self.user)
        self.assertEqual(margin_interest_records[1].amount, 100)
        self.assertEqual(margin_interest_records[1].margin_current, 1100)

        self.assertEqual(margin_penal_interest_records[0].user, self.user)
        self.assertEqual(margin_penal_interest_records[0].amount, 50)
        self.assertEqual(margin_penal_interest_records[0].margin_current, 3350)
