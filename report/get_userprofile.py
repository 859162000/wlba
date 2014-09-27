# -*- coding: utf-8 -*-

from django.utils import timezone
from report.reports import P2PUserReportGenerator

def gen_user(id):
    start_time = timezone.datetime(2014, 9, 10)
    end_time = timezone.now()
    try:
        P2PUserReportGenerator.generate_report(start_time, end_time, id=id)
    except:
        print u'生成错误'
