# coding=utf-8
from datetime import timedelta, datetime
import os
from os.path import join
from os import makedirs
import csv
import codecs
import cStringIO
import logging
from django.conf import settings
from report.crypto import ReportCrypto
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


class ReportGeneratorBase(object):
    @classmethod
    def get_file_path(cls, start_time, end_time):
        if hasattr(cls, 'prefix'):
            filename = '%s-%s.tsv' % (cls.prefix, start_time.strftime('%Y-%m-%d'))
            path = join('reports', cls.prefix, filename)
            return path
        else:
            raise AttributeError('Can\'t find attribute prefix')

    @classmethod
    def generate_report_content(cls, start_time, end_time):
        raise NotImplementedError()

    @classmethod
    def get_report_name(cls, start_time, end_time):
        if hasattr(cls, 'reportname_format'):
            return cls.reportname_format % (start_time.strftime('%Y-%m-%d'), end_time.strftime('%Y-%m-%d'))


    @classmethod
    def generate_report(cls, start_time, end_time=None):
        if end_time is None:
            end_time = start_time + timedelta(days=1)

        assert(isinstance(start_time, datetime))
        assert(isinstance(start_time, datetime))

        path = cls.get_file_path(start_time, end_time)
        absolute_path = os.path.join(settings.MEDIA_ROOT, path)
        folder, name = os.path.split(absolute_path)

        try:
            makedirs(folder)
        except OSError, e:
            if e.errno != 17:
                raise

        content = cls.generate_report_content(start_time, end_time)

        with open(absolute_path, 'w+b') as tsv_file:
            tsv_file.write(content)

        report = Report(name=cls.get_report_name(start_time, end_time))
        report.file = path
        report.content = content
        report.save()
        ReportCrypto.encrypt_file(absolute_path)
        return report


class DepositReportGenerator(ReportGeneratorBase):
    prefix = 'czjl'
    reportname_format = u'充值记录 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):

        output = cStringIO.StringIO()
        pay_infos = PayInfo.objects.filter(create_time__gte=start_time, create_time__lt=end_time, type='D').select_related('user').select_related('user__wanglibaouserprofile').select_related('order')
        writer = UnicodeWriter(output, delimiter='\t')
        writer.writerow(['Id', u'用户名', u'交易号', u'类型', u'充值银行', u'充值金额', u'充值手续费', u'实际到账金额', u'状态', u'操作时间', u'操作ip'])

        for pay_info in pay_infos:
            writer.writerow([
                str(pay_info.id),
                pay_info.user.wanglibaouserprofile.phone,
                str(pay_info.order.id),
                u'线上充值',
                unicode(pay_info.bank.name),
                str(pay_info.amount),
                str(pay_info.fee),
                str(pay_info.amount - pay_info.fee),
                unicode(pay_info.status),
                pay_info.create_time.strftime("%Y-%m-%d %H:%M"),
                str(pay_info.request_ip),
            ])

        return output.getvalue()


class WithDrawReportGenerator(ReportGeneratorBase):
    prefix = 'txjl'
    reportname_format = u'提现记录 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):
        payinfos = PayInfo.objects.filter(create_time__gte=start_time, create_time__lt=end_time, type='W', status=PayInfo.ACCEPTED).prefetch_related('user').prefetch_related('user__wanglibaouserprofile').prefetch_related('order')

        output = cStringIO.StringIO()

        writer = UnicodeWriter(output, delimiter='\t')
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
        return output.getvalue()


class PaybackReportGenerator(ReportGeneratorBase):
    prefix = 'hkjl'
    reportname_format = u'还款 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):
        output = cStringIO.StringIO()
        writer = UnicodeWriter(output, delimiter='\t')
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
        return output.getvalue()


class P2PAuditReportGenerator(ReportGeneratorBase):
    prefix = 'p2p_audit'
    reportname_format = u'满标复审 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):
        output = cStringIO.StringIO()

        writer = UnicodeWriter(output, delimiter='\t')
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
                unicode(product.name),
                str(product.total_amount),
                str(product.ordered_amount),
                str(product.expected_earning_rate),
                str(product.period),
                unicode(product.pay_method),
                u'抵押标', # Hard code this since it is not used anywhere except this table
                str(len(product.equities.all())),
                unicode(product.status),
                product.soldout_time.strftime("%Y-%m-%d %H:%M:%S"),
                unicode(product.borrower_name),
                unicode(product.borrower_phone),
                unicode(product.borrower_id_number),
                unicode(product.borrower_bankcard_bank_code),
                unicode(product.borrower_bankcard),
                unicode(product.borrower_bankcard_bank_province),
                unicode(product.borrower_bankcard_bank_city),
                unicode(product.borrower_bankcard_bank_branch)
            ])

        return output.getvalue()


class ReportGenerator(object):

    @classmethod
    def generate_reports(cls, start_time, end_time=None):
        DepositReportGenerator.generate_report(start_time=start_time, end_time=end_time)
        WithDrawReportGenerator.generate_report(start_time=start_time, end_time=end_time)
        PaybackReportGenerator.generate_report(start_time=start_time, end_time=end_time)
        P2PAuditReportGenerator.generate_report(start_time=start_time, end_time=end_time)
