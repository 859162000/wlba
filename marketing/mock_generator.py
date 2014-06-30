# coding=utf-8
from marketing.models import NewsAndReport


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