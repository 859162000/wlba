# coding=utf-8
from datetime import timedelta, datetime
from django.conf import settings
from os.path import join
from os import makedirs
from report.models import Report
from wanglibao_pay.models import PayInfo
import csv
import codecs, cStringIO


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class ReportGenerator(object):

    @classmethod
    def generate_deposit_report(self, start_time, end_time=None):
        if end_time is None:
            end_time = start_time + timedelta(days=1)

        assert(isinstance(start_time, datetime))
        assert(isinstance(start_time, datetime) or end_time is None)

        payinfos = PayInfo.objects.filter(create_time__gte=start_time, create_time__lt=end_time, type='D').prefetch_related('user').prefetch_related('user__wanglibaouserprofile').prefetch_related('order')

        filename = 'czjl-%s.tsv' % start_time.strftime('%Y-%m-%d')
        folder = join(settings.MEDIA_ROOT, 'reports', 'czjl')
        path = join(folder, filename)

        try:
            makedirs(folder)
        except OSError, e:
            if e.errno != 17:
                raise

        with open(path, 'w+b') as tsv_file:
            writer = UnicodeWriter(tsv_file, delimiter='\t')

            writer.writerow(['Id', u'用户名', u'交易号', u'类型', u'充值银行', u'充值金额', u'充值手续费', u'实际到账金额', u'状态', u'操作时间', u'操作ip'])

            for payinfo in payinfos:
                writer.writerow([
                    str(payinfo.id),
                    payinfo.user.wanglibaouserprofile.name,
                    str(payinfo.order.id),
                    u'线上充值',
                    payinfo.bank.name,
                    str(payinfo.amount),
                    str(payinfo.fee),
                    str(payinfo.amount - payinfo.fee),
                    u'待审核',
                    payinfo.create_time.strftime("%Y-%m-%d %H-%M"),
                    str(payinfo.request_ip),
                ])

            report = Report(name=u'充值记录 %s' % start_time.strftime('%Y-%m-%d %H-%M-%S'))
            report.file = join('reports', 'czjl', filename)
            report.save()

            return report

    @classmethod
    def generate_withdraw_report(self, start_time, end_time=None):
        if end_time is None:
            end_time = start_time + timedelta(days=1)

        assert(isinstance(start_time, datetime))
        assert(isinstance(start_time, datetime) or end_time is None)

        payinfos = PayInfo.objects.filter(create_time__gte=start_time, create_time__lt=end_time, type='W').prefetch_related('user').prefetch_related('user__wanglibaouserprofile').prefetch_related('order')

        filename = 'txjl-%s.tsv' % start_time.strftime('%Y-%m-%d')
        folder = join(settings.MEDIA_ROOT, 'reports', 'txjl')
        path = join(folder, filename)

        try:
            makedirs(folder)
        except OSError, e:
            if e.errno != 17:
                raise

        with open(path, 'w+b') as tsv_file:
            writer = UnicodeWriter(tsv_file, delimiter='\t')

            writer.writerow(['Id', u'用户名', u'真实姓名', u'身份证', u'手机', u'提现银行', u'支行', u'所在地', u'提现账号', u'提现总额', u'到账金额', u'手续费', u'提现时间', u'提现ip', u'状态'])

            for payinfo in payinfos:
                writer.writerow([
                    str(payinfo.id),
                    payinfo.user.wanglibaouserprofile.phone,
                    payinfo.account_name,
                    payinfo.user.wanglibaouserprofile.id_number,
                    payinfo.user.wanglibaouserprofile.phone,
                    payinfo.bank.name,
                    '-',
                    '-',
                    payinfo.card_no,
                    payinfo.total_amount,
                    payinfo.amount,
                    payinfo.fee,
                    payinfo.create_time.strftime("%Y-%m-%d %H-%M"),
                    str(payinfo.request_ip),
                    u'申请'
                ])

            report = Report(name=u'充值记录 %s' % start_time.strftime('%Y-%m-%d %H-%M-%S'))
            report.file = join('reports', 'txjl', filename)
            report.save()

            return report
