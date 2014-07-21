# coding=utf-8
from datetime import timedelta, datetime
from os.path import join
from os import makedirs
import csv
import codecs
import cStringIO
import logging

from django.conf import settings

from report.models import Report
from wanglibao_p2p.models import UserAmortization, P2PProduct
from wanglibao_pay.models import PayInfo


logger = logging.getLogger(__name__)


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
    def generate_reports(cls, start_time, end_time=None):
        cls.generate_deposit_report(start_time=start_time, end_time=end_time)
        cls.generate_withdraw_report(start_time=start_time, end_time=end_time)
        cls.generate_payback_report(start_time=start_time, end_time=end_time)
        cls.generate_p2p_audit_report(start_time=start_time, end_time=end_time)


    @classmethod
    def generate_deposit_report(cls, start_time, end_time=None):
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
                    payinfo.create_time.strftime("%Y-%m-%d %H:%M"),
                    str(payinfo.request_ip),
                ])

            report = Report(name=u'充值记录 %s' % start_time.strftime('%Y-%m-%d %H:%M:%S'))
            report.file = join('reports', 'czjl', filename)
            report.save()

            return report

    @classmethod
    def generate_withdraw_report(cls, start_time, end_time=None):
        if end_time is None:
            end_time = start_time + timedelta(days=1)

        assert(isinstance(start_time, datetime))
        assert(isinstance(start_time, datetime) or end_time is None)

        payinfos = PayInfo.objects.filter(create_time__gte=start_time, create_time__lt=end_time, type='W', status=PayInfo.ACCEPTED).prefetch_related('user').prefetch_related('user__wanglibaouserprofile').prefetch_related('order')

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
                    str(payinfo.total_amount),
                    str(payinfo.amount),
                    str(payinfo.fee),
                    payinfo.create_time.strftime("%Y-%m-%d %H:%M"),
                    str(payinfo.request_ip),
                    unicode(payinfo.status)
                ])

            report = Report(name=u'提现记录 %s' % start_time.strftime('%Y-%m-%d %H:%M:%S'))
            report.file = join('reports', 'txjl', filename)
            report.save()

            return report

    @classmethod
    def generate_payback_report(cls, start_time, end_time=None):
        if end_time is None:
            end_time = start_time + timedelta(days=1)

        assert(isinstance(start_time, datetime))
        assert(isinstance(start_time, datetime) or end_time is None)

        fileprefix = 'pay'

        filename = '%s-%s.tsv' % (fileprefix, start_time.strftime('%Y-%m-%d'))
        folder = join(settings.MEDIA_ROOT, 'reports', fileprefix)
        path = join(folder, filename)

        try:
            makedirs(folder)
        except OSError, e:
            if e.errno != 17:
                raise

        with open(path, 'w+b') as tsv_file:
            writer = UnicodeWriter(tsv_file, delimiter='\t')

            writer.writerow([u'序号', u'贷款号', u'借款人', u'借款标题', u'借款期数', u'借款类型', u'应还日期',
                             u'应还本息', u'应还本金', u'应还利息', u'状态'])

            amortizations = UserAmortization.objects.filter(term_date__gte=start_time, term_date__lt=end_time, settled=False)\
                .prefetch_related('product_amortization').prefetch_related('product_amortization__product')\
                .prefetch_related('user').prefetch_related('user__wanglibaouserprofile')

            for index, amortization in enumerate(amortizations):
                writer.writerow([
                    str(index + 1),
                    amortization.product_amortization.product.serial_number,
                    amortization.product_amortization.product.serial_number + '_JK',
                    amortization.product_amortization.product.name,
                    u'第%d期' % amortization.term,
                    u'抵押标',
                    amortization.term_date.strftime("%Y-%m-%d"),
                    str(amortization.principal + amortization.interest),
                    str(amortization.principal),
                    str(amortization.interest),
                    u'待还',
                    amortization.term_date.strftime("%Y-%m-%d")
                ])

            report = Report(name=u'还款列表 %s' % start_time.strftime('%Y-%m-%d %H:%M:%S'))
            report.file = join('reports', fileprefix, filename)
            report.save()

            return report


    @classmethod
    def generate_p2p_audit_report(cls, start_time, end_time=None):
        if end_time is None:
            end_time = start_time + timedelta(days=1)

        assert(isinstance(start_time, datetime))
        assert(isinstance(start_time, datetime) or end_time is None)

        fileprefix = 'p2p_audit'

        filename = '%s-%s.tsv' % (fileprefix, start_time.strftime('%Y-%m-%d'))
        folder = join(settings.MEDIA_ROOT, 'reports', fileprefix)
        path = join(folder, filename)

        try:
            makedirs(folder)
        except OSError, e:
            if e.errno != 17:
                raise

        with open(path, 'w+b') as tsv_file:
            writer = UnicodeWriter(tsv_file, delimiter='\t')

            writer.writerow([u'序号', u'贷款号', u'用户名称', u'借款标题', u'借款金额', u'已借金额', u'利率', u'借款期限', u'还款方式',
                             u'借款类型', u'投资次数', u'状态', u'满标时间', u'真实姓名', u'手机号', u'身份证', u'银行名', u'银行账号',
                             u'省份', u'地区', u'支行'])

            # Get all products with status 满标待打款
            products = P2PProduct.objects.filter(status=u'满标待打款')

            for index, product in enumerate(products):
                writer.writerow([
                    str(index + 1),
                    product.serial_number,
                    '-',
                    product.name,
                    str(product.total_amount),
                    str(product.ordered_amount),
                    str(product.expected_earning_rate),
                    str(product.period),
                    product.pay_method,
                    '抵押标', # Hard code this since it is not used anywhere except this table
                    str(len(product.equities.all())),
                    product.status,
                    product.soldout_time.strftime("%Y-%m-%d %H:%M:%S"),
                    product.borrower_name,
                    product.borrower_phone,
                    product.borrower_id_number,
                    product.borrower_bankcard_bank_code,
                    product.borrower_bankcard,
                    product.borrower_bankcard_province,
                    product.borrower_bankcard_city,
                    product.borrower_bankcard_branch
                ])

            report = Report(name=u'满标复审 %s' % start_time.strftime('%Y-%m-%d %H:%M:%S'))
            report.file = join('reports', fileprefix, filename)
            report.save()

            return report