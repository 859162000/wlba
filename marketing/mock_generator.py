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
        count = 0
        while count <= item_counts:
            letters = 'abcdefghijkmnpqrstuvwxyzABCDEFGHIJKMNPQRSTUVWXYZ'
            digits = '23456789'
            salt = ''.join(random.sample(letters+digits, 6))
            insert_flag = False
            try:
                invite_code = InviteCode.objects.create(code=salt)
                invite_code.save()
                insert_flag = True
            except IntegrityError, e:
                logging.debug(e)

            if insert_flag:
                count += 1
        logging.debug('code inserted has been done')
