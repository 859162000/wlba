# coding=utf-8
import string
import random
import logging
from django.utils import timezone
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
                       for salt in list(set([''.join(random.sample(letters + digits, 6))
                                             for i in range(item_counts)]))]
        InviteCode.objects.bulk_create(insert_list)
        logging.debug('code inserted has been done')

    @classmethod
    def check_and_generate_codes(cls, check_counts=50000, item_counts=20000):
        total_num = InviteCode.objects.filter(is_used=False).count()
        if total_num < check_counts:
            letters = 'abcdefghijkmnpqrstuvwxyz'
            digits = '23456789'
            insert_list = []
            generate_list = [salt for salt in list(set([''.join(random.sample(letters + digits, 6))
                                                        for i in range(item_counts)]))]
            num = 0
            for code in generate_list:
                try:
                    InviteCode.objects.get(code=code)
                except InviteCode.DoesNotExist:
                    insert_list.append(InviteCode(code=code))
                    num += 1

            InviteCode.objects.bulk_create(insert_list)

            # 发送提醒短信
            from wanglibao_sms.tasks import send_messages
            message = u'原始邀请码少于{}条,系统已重新生成{}条'.format(check_counts, num)
            phones_list = ['15038038823', '18612250386']
            messages_list = [message]
            send_messages.apply_async(kwargs={
                "phones": phones_list,
                "messages": messages_list
            })

            logging.debug('code inserted has been done, total items: {}'.format(num))

    @classmethod
    def generate_reward(cls, item_counts, type, description):
        """ type=u'一个月迅雷会员'
            description=u'迅雷活动赠送会员'
        """
        end_time = timezone.datetime(2015, 1, 1)
        salt = [''.join(random.sample(string.ascii_letters + string.digits, 8))
                for i in range(item_counts)]
        salt_list = list(set(salt))
        insert_list = [Reward(type=type, description=description, content=salt, end_time=end_time)
                       for salt in salt_list]
        Reward.objects.bulk_create(insert_list)
        logging.debug('reword has been done')
