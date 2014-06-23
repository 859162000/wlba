# encoding: utf-8
import json
from datetime import date, timedelta
from django.test import TestCase, TransactionTestCase
from  ext import P2PTerm, P2PPeriod
# Create your tests here.


day = date(2014, 05, 01)


class P2PPeriodTest(TestCase):

    def setUp(self):
        self.term0 = P2PTerm(day)
        self.term1 = P2PTerm(day-timedelta(days=1), paid=True)
        self.term2 = P2PTerm(day-timedelta(days=2), delay=True)
        self.term3 = P2PTerm(day-timedelta(days=3), paid=True, delay=True)
        self.period0 = P2PPeriod([self.term0, self.term1, self.term2, self.term3])
        self.term0dict = {
            'date': '2014-05-01',
            'paid': False,
            'delay': False
        }
        self.term1dict = {
            'date': '2014-04-30',
            'paid': True,
            'delay': False
        }
        self.term2dict = {
            'date': '2014-04-29',
            'paid': False,
            'delay': True
        }
        self.term3dict = {
            'date': '2014-04-28',
            'paid': True,
            'delay': True
        }
        self.period0dict = {
            'count': 4,
            'terms': [self.term0.serializer(), self.term1.serializer(),
                      self.term2.serializer(), self.term3.serializer()]
        }

    def testTermStatus(self):
        self.assertEqual(self.term0.status, u'未到还款期限')
        self.assertEqual(self.term1.status, u'已还')
        self.assertEqual(self.term2.status, u'逾期未还')
        self.assertEqual(self.term3.status, u'逾期已还')

    def testTermSerializer(self):
        self.assertEqual(self.term0.serializer(), self.term0dict)
        self.assertEqual(self.term1.serializer(), self.term1dict)
        self.assertEqual(self.term2.serializer(), self.term2dict)
        self.assertEqual(self.term3.serializer(), self.term3dict)

    def testTermToJson(self):
        self.assertEqual(self.term0.to_json(), json.dumps(self.term0dict))
        self.assertEqual(self.term1.to_json(), json.dumps(self.term1dict))
        self.assertEqual(self.term2.to_json(), json.dumps(self.term2dict))
        self.assertEqual(self.term3.to_json(), json.dumps(self.term3dict))

    def testPeriodCount(self):
        self.assertEqual(self.period0.count, 4)
        term = self.period0.terms.pop()
        self.assertEqual(self.period0.count, 3)
        self.period0.terms.append(term)
        self.assertEqual(self.period0.count, 4)

    def testPeriodSerializer(self):
        self.assertEqual(self.period0.serializer(), self.period0dict)

    def testPeriodToJson(self):
        self.assertEqual(self.period0.to_json(), json.dumps(self.period0dict))
