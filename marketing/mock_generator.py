# coding=utf-8
import string
import random
import logging

from marketing.models import NewsAndReport
from marketing.models import InviteCode, Reward


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

        letters = 'abcdefghijkmnpqrstuvwxyz'
        digits = '23456789'
        # salt = [''.join(random.sample(letters+digits, 6)) for i in range(item_counts)]
        # salt_list = list(set(salt))
        # insert_list = [InviteCode(code=salt) for salt in salt_list]
        insert_list = [InviteCode(code=salt)
                       for salt in list(set([''.join(random.sample(letters+digits, 6))
                                             for i in range(item_counts)]))]
        InviteCode.objects.bulk_create(insert_list)
        logging.debug('code inserted has been done')

    @classmethod
    def generate_reward(cls, item_counts, type, description):
        """ type=u'一个月迅雷会员'
            description=u'迅雷活动赠送会员'
        """
        salt = [''.join(random.sample(string.ascii_letters+string.digits, 8))
                for i in range(item_counts)]
        salt_list = list(set(salt))
        insert_list = [Reward(type=type, description=description, content=salt)
                        for salt in salt_list]
        Reward.objects.bulk_create(insert_list)
        logging.debug('reword has been done')
