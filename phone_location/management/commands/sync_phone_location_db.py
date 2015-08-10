# -*- coding=utf-8 -*-
from django.core.management.base import BaseCommand
from phone_location.models import PhoneLocation
import urllib2


def run():

    check_list = [130, 131, 132, 133, 134, 135, 136, 137, 138, 139,
                  145, 147,
                  150, 151, 152, 153, 155, 156, 157, 158, 159,
                  170, 175, 176, 177,
                  180, 181, 182, 183, 185, 186, 187, 188, 189]

    for pre in check_list:

        for i in range(0, 2):
            num = int(str(pre) + str("%.4d" % i))
            response = urllib2.urlopen("http://cx.shouji.360.cn/phonearea.php?number=%d" % num)
            res = response.read()
            d = eval(res)

            province = eval('u"'+d['data']['province']+'"')
            city = eval('u"'+d['data']['city']+'"')
            sp = eval('u"'+d['data']['sp']+'"')

            if province:
                PhoneLocation.objects.get_or_create(tel=num, province=province, city=city, sp=sp)
            else:
                print 'unknown number ', num
        print 'end of ', pre
    print 'end of check'


class Command(BaseCommand):

    def handle(self, *args, **options):

        check_list = [130, 131, 132, 133, 134, 135, 136, 137, 138, 139,
                      145, 147,
                      150, 151, 152, 153, 155, 156, 157, 158, 159,
                      170, 175, 176, 177,
                      180, 181, 182, 183, 185, 186, 187, 188, 189]

        for pre in check_list:
            for i in range(0, 10000):
                num = int(str(pre) + str("%.4d" % i))
                response = urllib2.urlopen("http://cx.shouji.360.cn/phonearea.php?number=%d" % num)
                res = response.read()
                d = eval(res)

                province = eval('u"'+d['data']['province']+'"')
                city = eval('u"'+d['data']['city']+'"')
                sp = eval('u"'+d['data']['sp']+'"')

                if province:
                    PhoneLocation.objects.get_or_create(tel=num, province=province, city=city, sp=sp)
                else:
                    print 'unknown number', num
            print 'end of ', pre
        print 'end of check'
