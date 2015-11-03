# encoding:utf-8
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

# Create your tests here.
from marketing.models import IntroducedBy
from wanglibao_sms.utils import send_validation_code


class TestMarketingAPI(TestCase):
    def setUp(self):
        pass

    def test_quick_applyer(self):
        response = self.client.post("/api/quick/applyer/",
                         {
                            'phone':13521522034,
                             'name':'hello',
                             'address': u'北京',
                             'apply_way': 0,
                             'amount': '10-30'
                         }
                         )
        print response.content

    def test_gift_owner(self):
        response = self.client.post("/api/gift/owner/?promo_token=jcw",
                        {
                            'phone': 13423444354,
                            'name': 'Yihen',
                            'address': u"北京市朝阳区"
                        })
        print "Hello world"
        print response.content
        print "Hello world"
