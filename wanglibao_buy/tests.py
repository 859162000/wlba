# encoding:utf-8

import json
from django.test import TestCase
from rest_framework import status
from wanglibao_buy.models import TradeInfo
from wanglibao_fund.models import Fund
from wanglibao_sms.models import PhoneValidateCode
from wanglibao_fund.mock_generator import MockGenerator


class TradeInfoAPITest(TestCase):
    def test_trade_info_api(self):
        phone = '13811111111'
        password = 'wanglibank'

        response = self.client.post('/api/phone_validation_code/%s/' % phone, {})

        self.assertEqual(response.status_code, 200)

        validate_code = PhoneValidateCode.objects.all()[0].validate_code

        self.client.post('/api/register/', {
            'identifier': phone,
            'password': password,
            'validate_code': validate_code,
            'nickname': 'nickname'
        })

        self.client.login(identifier=phone, password=password)

        MockGenerator.generate_fund_issuers(count=1)
        MockGenerator.generate_fund(count=1)

        fund = Fund.objects.all().first()

        response = self.client.post('/api/trade_info/', json.dumps({
            'type': 'fund',
            'trade_type': u'申购',
            'item_id': fund.id,
            'item_name': u'测试名字',
            'amount': 3000,
            'user': 1,
            'verify_info': '1321412412321',
            'related_info': '扣款时间 你不知道'
        }), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        fund = Fund.objects.all().get(pk=fund.id)
        self.assertEqual(fund.bought_people_count, 1)
        self.assertEqual(fund.bought_count, 1)
        self.assertEqual(fund.bought_amount, 3000)

        response = self.client.post('/api/trade_info/', json.dumps({
            'type': 'fund',
            'trade_type': u'申购',
            'item_id': fund.id,
            'item_name': u'测试名字',
            'amount': 3000,
            'user': 1,
            'verify_info': '1321412412321',
            'related_info': '扣款时间 你不知道'
        }), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        fund = Fund.objects.all().get(pk=fund.id)
        self.assertEqual(fund.bought_people_count, 1)
        self.assertEqual(fund.bought_count, 2)
        self.assertEqual(fund.bought_amount, 6000)

        self.client.post('/api/trade_info/', json.dumps({
            'type': 'fund',
            'trade_type': u'申购',
            'fund_code': fund.product_code,
            'item_name': u'测试名字',
            'amount': 3000,
            'user': 1,
            'verify_info': '1321412412321',
            'related_info': '扣款时间 你不知道'
        }), content_type="application/json")

        fund = Fund.objects.all().get(pk=fund.id)
        self.assertEqual(fund.bought_people_count, 1)
        self.assertEqual(fund.bought_count, 3)
