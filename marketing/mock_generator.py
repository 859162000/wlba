# coding=utf-8
from marketing.models import NewsAndReport
from django.db import IntegrityError
import string, random, logging
from marketing.models import InviteCode


logging.basicConfig(level=logging.DEBUG)

class MockGenerator(object):
    @classmethod
    def generate_news(cls, clean=False):
        if clean:
            NewsAndReport.objects.all().delete()

        for i in range(0, 20):
            n = NewsAndReport()
            n.name = u'报道%d' % (i + 1)
            n.link = 'http://www.baidu.com'

            n.save()

    @classmethod
    def generate_codes(cls, item_counts):

        letters = 'abcdefghijkmnpqrstuvwxyzABCDEFGHIJKMNPQRSTUVWXYZ'
        digits = '23456789'
        salt = [''.join(random.sample(letters+digits, 6)) for i in range(item_counts)]
        salt_list = list(set(salt))
        insert_list = [InviteCode(code=salt) for salt in salt_list]


        InviteCode.objects.bulk_create(insert_list)
        logging.debug('code inserted has been done')
