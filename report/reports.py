# coding=utf-8
from datetime import timedelta, datetime
from os.path import join
import csv
import codecs
import cStringIO
import logging
from django.core.files.base import ContentFile
from django.core.files.storage import DefaultStorage
from marketing.models import IntroducedBy
from report.crypto import ReportCrypto
from report.models import Report
from wanglibao_p2p.models import UserAmortization, P2PProduct, ProductAmortization, P2PRecord, Earning
from wanglibao_pay.models import PayInfo
from wanglibao_margin.models import MarginRecord
from django.utils import timezone
from django.contrib.auth.models import User
from wanglibao_margin.models import Margin
from django.db.models import Sum
from marketing.models import ClientData
from wanglibao_redpack.models import RedPackRecord

logger = logging.getLogger(__name__)
storage = DefaultStorage()


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
            filename = '%s-%s-%s.tsv' % (cls.prefix, start_time.strftime('%Y-%m-%d'), end_time.strftime('%Y-%m-%d'))
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
            return cls.reportname_format % (
                start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'))


    @classmethod
    def generate_report(cls, start_time, end_time=None, **kwargs):
        if end_time is None:
            end_time = start_time + timedelta(days=1)

        assert (isinstance(start_time, datetime))
        assert (isinstance(start_time, datetime))

        path = cls.get_file_path(start_time, end_time)

        if kwargs.get('type'):
            content = cls.generate_report_content(start_time, end_time, kwargs.get('type'))
        else:
            content = cls.generate_report_content(start_time, end_time)

        encrypted_content = ReportCrypto.encrypt_file(content)
        path = storage.save(path, ContentFile(encrypted_content))

        report = Report(name=cls.get_report_name(start_time, end_time))
        report.file = path
        report.content = content
        report.save()
        return report


class DepositReportGenerator(ReportGeneratorBase):
    prefix = 'czjl'
    reportname_format = u'充值记录 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):
        output = cStringIO.StringIO()
        pay_infos = PayInfo.objects.filter(create_time__gte=start_time, create_time__lt=end_time, type='D') \
            .select_related('user').select_related('user__wanglibaouserprofile').select_related('order')
        writer = UnicodeWriter(output, delimiter='\t')
        writer.writerow(['Id', u'用户名', u'交易号', u'类型', u'充值银行', u'充值金额', u'充值手续费', u'实际到账金额',
                         u'状态', u'操作时间', u'操作ip', u'编号'])

        for pay_info in pay_infos:
            bank_name = pay_info.bank.name if pay_info.bank else ''

            writer.writerow([
                str(pay_info.id),
                pay_info.user.wanglibaouserprofile.phone,
                str(pay_info.order.id),
                u'线上充值',
                unicode(bank_name),
                str(pay_info.amount),
                str(pay_info.fee),
                str(pay_info.amount - pay_info.fee),
                unicode(pay_info.status),
                timezone.localtime(pay_info.create_time).strftime("%Y-%m-%d %H:%M:%S"),
                unicode(pay_info.request_ip),
                unicode(pay_info.uuid)
            ])
        return output.getvalue()


class WithDrawReportGenerator(ReportGeneratorBase):
    prefix = 'txjl'
    reportname_format = u'提现记录 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):
        payinfos = PayInfo.objects.filter(create_time__gte=start_time, create_time__lt=end_time, type='W',
                                          status__in=[PayInfo.SUCCESS, PayInfo.ACCEPTED]) \
            .prefetch_related('user').prefetch_related('user__wanglibaouserprofile').prefetch_related('order')

        output = cStringIO.StringIO()

        writer = UnicodeWriter(output, delimiter='\t')
        writer.writerow(['Id', u'用户名', u'真实姓名', u'身份证', u'手机', u'提现银行', u'支行', u'所在地', u'提现账号',
                         u'提现总额', u'到账金额', u'手续费', u'提现时间', u'提现ip', u'状态', u'审核时间', u'编号'])

        for payinfo in payinfos:
            confirm_time = ""
            if payinfo.confirm_time:
                confirm_time = timezone.localtime(payinfo.confirm_time).strftime("%Y-%m-%d %H:%M:%S")

            bank_name = payinfo.bank.name if payinfo.bank else ''

            writer.writerow([
                str(payinfo.id),
                payinfo.user.wanglibaouserprofile.phone,
                payinfo.account_name,
                payinfo.user.wanglibaouserprofile.id_number,
                payinfo.user.wanglibaouserprofile.phone,
                bank_name,
                '-',
                '-',
                payinfo.card_no,
                str(payinfo.total_amount),
                str(payinfo.amount),
                str(payinfo.fee),
                timezone.localtime(payinfo.create_time).strftime("%Y-%m-%d %H:%M:%S"),
                str(payinfo.request_ip),
                unicode(payinfo.status),
                confirm_time,
                unicode(payinfo.uuid)
            ])
        return output.getvalue()


class WithDrawDetailReportGenerator(ReportGeneratorBase):
    prefix = 'txxxjl'
    reportname_format = u'提现详细记录 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):
        margins = MarginRecord.objects.filter(catalog__icontains=u'取款',
                                              create_time__gte=start_time, create_time__lt=end_time) \
            .prefetch_related('user').prefetch_related('user__wanglibaouserprofile')

        output = cStringIO.StringIO()

        writer = UnicodeWriter(output, delimiter='\t')
        writer.writerow(['Id', u'用户名', u'真实姓名', u'身份证', u'手机', u'提现银行', u'支行', u'所在地', u'提现账号',
                         u'提现总额', u'到账金额', u'手续费', u'提现时间', u'提现ip', u'状态', u'编号'])

        for margin in margins:
            payinfo = margin.payinfo_set.all().first()
            bank_name = payinfo.bank.name if payinfo.bank else ''

            writer.writerow([
                str(margin.id),
                margin.user.username,
                margin.user.wanglibaouserprofile.name,
                margin.user.wanglibaouserprofile.id_number,
                margin.user.wanglibaouserprofile.phone,
                bank_name,
                '-',
                '-',
                margin.payinfo_set.first().card_no,
                str(margin.payinfo_set.first().total_amount),
                str(margin.payinfo_set.first().amount),
                str(margin.payinfo_set.first().fee),
                timezone.localtime(margin.payinfo_set.first().create_time).strftime("%Y-%m-%d %H:%M:%S"),
                str(margin.payinfo_set.first().request_ip),
                unicode(margin.payinfo_set.first().status),
                unicode(margin.payinfo_set.first().uuid)
            ])

        return output.getvalue()


class ProductionRecordReportGenerator(ReportGeneratorBase):
    prefix = 'cpls'
    reportname_format = u'产品流水 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):

        p2precords = P2PRecord.objects.filter(create_time__gte=start_time, create_time__lt=end_time) \
            .prefetch_related('user').prefetch_related('user__wanglibaouserprofile')

        output = cStringIO.StringIO()

        writer = UnicodeWriter(output, delimiter='\t')
        writer.writerow([u'序号', u'流水类型', u'关联订单号', u'p2p产品', u'购买者', u'购买者手机号',
                         u'发生数', u'标后余额', u'发生时间', u'摘要', u'编号'])
        name = ''
        phone = ''
        for index, p2precord in enumerate(p2precords):
            if p2precord.user:
                name = p2precord.user.wanglibaouserprofile.name
                phoen = p2precord.user.wanglibaouserprofile.phone
            writer.writerow([
                str(index + 1),
                p2precord.catalog,
                unicode(p2precord.order_id),
                p2precord.product.name,
                name,
                phone,
                unicode(p2precord.amount),
                unicode(p2precord.product_balance_after),
                timezone.localtime(p2precord.create_time).strftime("%Y-%m-%d %H:%M:%S"),
                p2precord.description,
                unicode("wanglibao_cpls_" + str(p2precord.id))
            ])
        return output.getvalue()


class PaybackReportGenerator(ReportGeneratorBase):
    prefix = 'yhhkjl'
    reportname_format = u'用户还款计划 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):
        output = cStringIO.StringIO()
        writer = UnicodeWriter(output, delimiter='\t')
        writer.writerow([u'序号', u'贷款号', u'借款人', u'借款标题', u'借款期数', u'借款类型', u'应还日期',
                         u'应还本息', u'应还本金', u'应还利息', u'状态', u'编号'])

        amortizations = UserAmortization.objects.filter(term_date__gte=start_time, term_date__lt=end_time) \
            .prefetch_related('product_amortization').prefetch_related('product_amortization__product') \
            .prefetch_related('user').prefetch_related('user__wanglibaouserprofile')

        for index, amortization in enumerate(amortizations):
            writer.writerow([
                str(index + 1),
                amortization.product_amortization.product.serial_number,
                amortization.product_amortization.product.serial_number + '_JK',
                amortization.product_amortization.product.name,
                u'第%d期' % amortization.term,
                u'抵押标',
                timezone.localtime(amortization.term_date).strftime("%Y-%m-%d %H:%M:%S"),
                str(amortization.principal + amortization.interest),
                str(amortization.principal),
                str(amortization.interest),
                # u'待还',
                amortization.product_amortization.product.status,
                timezone.localtime(amortization.term_date).strftime("%Y-%m-%d %H:%M:%S"),
                unicode("wanglibao_yhhkjl_" + str(amortization.id))
            ])
        return output.getvalue()


class ProductionAmortizationsReportGenerator(ReportGeneratorBase):
    prefix = 'cphkjl'
    reportname_format = u'产品还款计划 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):
        output = cStringIO.StringIO()
        writer = UnicodeWriter(output, delimiter='\t')
        writer.writerow([u'序号', u'贷款号', u'借款人', u'借款标题', u'借款期数', u'借款类型', u'应还日期',
                         u'应还本息', u'应还本金', u'应还利息', u'状态', u'编号', u'备注', u'借款企业/个人'])

        amortizations = ProductAmortization.objects.filter(
            term_date__gte=start_time, term_date__lt=end_time, product__status=u'还款中', settled=False)

        for index, amortization in enumerate(amortizations):
            writer.writerow([
                str(index + 1),
                amortization.product.serial_number,
                amortization.product.borrower_name,
                amortization.product.name,
                u'第%d期' % amortization.term,
                u'抵押标',
                timezone.localtime(amortization.term_date).strftime("%Y-%m-%d %H:%M:%S"),
                str(amortization.principal + amortization.interest),
                str(amortization.principal),
                str(amortization.interest),
                u'待还',
                unicode("wanglibao_cphkjl_" + str(amortization.id)),
                amortization.product.warrant_company.name,
                amortization.product.brief
            ])
        return output.getvalue()


class ProductionAmortizationsReportAllGenerator(ReportGeneratorBase):
    prefix = 'cphkjhall'
    reportname_format = u'产品还款计划All %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):
        output = cStringIO.StringIO()
        writer = UnicodeWriter(output, delimiter='\t')
        writer.writerow([u'借款编号', u'借款标题', u'借款企业/借款人', u'借款金额', u'满标时间', u'放款时间',
                         u'借款期数', u'还款时间', u'已还本金', u'已还利息', u'未还本金', u'未还利息', u'额外罚息', u'标的状态'])

        amortizations = ProductAmortization.objects.filter(
            product__publish_time__gte=start_time, product__publish_time__lt=end_time).order_by('-product', 'term')

        for index, amortization in enumerate(amortizations):
            if amortization.settled:
                principal_yes = str(amortization.principal)
                interest_yes = str(amortization.interest)
                principal_no = str(0)
                interest_no = str(0)
            else:
                principal_yes = str(0)
                interest_yes = str(0)
                principal_no = str(amortization.principal)
                interest_no = str(amortization.interest)
            if amortization.term_date:
                term_date = timezone.localtime(amortization.term_date).strftime("%Y-%m-%d %H:%M:%S")
            else:
                term_date = ''
            if amortization.product.soldout_time:
                soldout_time = timezone.localtime(amortization.product.soldout_time).strftime("%Y-%m-%d %H:%M:%S")
            else:
                soldout_time = ''
            if amortization.product.make_loans_time:
                make_loans_time = timezone.localtime(amortization.product.make_loans_time).strftime("%Y-%m-%d %H:%M:%S")
            else:
                make_loans_time = ''

            writer.writerow([
                amortization.product.serial_number,
                amortization.product.name,
                amortization.product.borrower_name,
                str(amortization.product.total_amount),
                soldout_time,
                make_loans_time,
                u'第%d期' % amortization.term,
                term_date,
                principal_yes,
                interest_yes,
                principal_no,
                interest_no,
                str(amortization.penal_interest),
                amortization.product.status
            ])
        return output.getvalue()


class ProductionAmortizationsSettledReportGenerator(ReportGeneratorBase):
    prefix = 'hkjijs'
    reportname_format = u'产品还款结算 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):
        output = cStringIO.StringIO()
        writer = UnicodeWriter(output, delimiter='\t')
        writer.writerow([u'序号', u'贷款号', u'借款人', u'借款类型', u'还款金额', u'状态', u'操作时间', u'编号'])

        amortizations = ProductAmortization.objects.filter(term_date__gte=start_time, term_date__lt=end_time) \
            .filter(settled=True)

        for index, amortization in enumerate(amortizations):
            writer.writerow([
                str(index + 1),
                amortization.product.serial_number,
                amortization.product.borrower_name,
                u'抵押标',
                str(amortization.principal + amortization.interest),
                u'成功',
                timezone.localtime(amortization.settlement_time).strftime("%Y-%m-%d %H:%M:%S"),
                unicode("wanglibao_hkjijs_" + str(amortization.id))
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
                         u'银行卡类型', u'省份', u'地区', u'支行'])

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
                u'抵押标',  # Hard code this since it is not used anywhere except this table
                str(len(product.equities.all())),
                unicode(product.status),
                (
                    product.soldout_time and timezone.localtime(product.soldout_time).strftime(
                        "%Y-%m-%d %H:%M:%S")) or '-',
                unicode(product.borrower_name),
                unicode(product.borrower_phone),
                unicode(product.borrower_id_number),
                unicode(product.borrower_bankcard_bank_code),
                unicode(product.borrower_bankcard),
                unicode(product.borrower_bankcard_type),
                unicode(product.borrower_bankcard_bank_province),
                unicode(product.borrower_bankcard_bank_city),
                unicode(product.borrower_bankcard_bank_branch)
            ])

        return output.getvalue()


class P2PstatusReportGenerator(ReportGeneratorBase):
    prefix = 'mbztbh'
    reportname_format = u'满标状态变化 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):
        output = cStringIO.StringIO()

        writer = UnicodeWriter(output, delimiter='\t')
        writer.writerow([u'序号', u'贷款号', u'用户名称', u'借款标题', u'借款金额', u'已借金额', u'利率', u'借款期限', u'还款方式',
                         u'投资次数', u'状态', u'满标时间', u'真实姓名', u'手机号', u'身份证', u'银行名', u'银行账号',
                         u'银行卡类型', u'省份', u'地区', u'支行'])

        p2precords = P2PRecord.objects.filter(catalog=u'状态变化', create_time__gte=start_time, create_time__lt=end_time)

        for index, p2precord in enumerate(p2precords):
            writer.writerow([
                str(index + 1),
                p2precord.product.serial_number,
                '-',
                unicode(p2precord.product.name),
                str(p2precord.product.total_amount),
                str(p2precord.product.ordered_amount),
                str(p2precord.product.expected_earning_rate),
                str(p2precord.product.period),
                unicode(p2precord.product.pay_method),
                str(len(p2precord.product.equities.all())),
                unicode(p2precord.product.status),
                (p2precord.product.soldout_time and timezone.localtime(p2precord.product.soldout_time).strftime(
                    "%Y-%m-%d %H:%M:%S")) or '-',
                unicode(p2precord.product.borrower_name),
                unicode(p2precord.product.borrower_phone),
                unicode(p2precord.product.borrower_id_number),
                unicode(p2precord.product.borrower_bankcard_bank_code),
                unicode(p2precord.product.borrower_bankcard),
                unicode(p2precord.product.borrower_bankcard_type),
                unicode(p2precord.product.borrower_bankcard_bank_province),
                unicode(p2precord.product.borrower_bankcard_bank_city),
                unicode(p2precord.product.borrower_bankcard_bank_branch)
            ])

        return output.getvalue()


class EearningReportGenerator(ReportGeneratorBase):
    prefix = 'zsjljs'
    reportname_format = u'赠送记录 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time, type=None):
        output = cStringIO.StringIO()
        writer = UnicodeWriter(output, delimiter='\t')
        writer.writerow([u'序号', u'用户姓名', u'用户手机号', u'p2p的id', u'p2p名',
                         u'收益金额', u'订单号', u'交易流水id', u'是否打款', u'类型', u'创建时间', u'更新时间', u'审核时间'])

        if type:
            earnings = Earning.objects.filter(create_time__gte=start_time, create_time__lt=end_time, type=type)
        else:
            earnings = Earning.objects.filter(create_time__gte=start_time, create_time__lt=end_time)

        for index, earning in enumerate(earnings):
            confirm_time = timezone.localtime(earning.confirm_time).strftime(
                "%Y-%m-%d %H:%M:%S") if earning.confirm_time else ''

            writer.writerow([
                str(index + 1),
                earning.user.wanglibaouserprofile.name,
                earning.user.wanglibaouserprofile.phone,
                str(earning.product_id),
                earning.product.short_name,
                str(earning.amount),
                str(earning.order_id),
                str(earning.margin_record_id),
                str(earning.type),
                str(earning.paid),
                timezone.localtime(earning.create_time).strftime("%Y-%m-%d %H:%M:%S"),
                timezone.localtime(earning.update_time).strftime("%Y-%m-%d %H:%M:%S"),
                confirm_time
            ])
        return output.getvalue()


class MarginReportGenerator(ReportGeneratorBase):
    prefix = 'yhje'
    reportname_format = u'用户金额 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):
        output = cStringIO.StringIO()
        writer = UnicodeWriter(output, delimiter='\t')
        writer.writerow([u'用户余额', u'冻结金额', u'提款中金额'])

        margin = Margin.objects.all().aggregate(Sum('margin'))['margin__sum']
        freeze = Margin.objects.all().aggregate(Sum('freeze'))['freeze__sum']
        withdrawing = Margin.objects.all().aggregate(Sum('withdrawing'))['withdrawing__sum']

        writer.writerow([
            str(margin),
            str(freeze),
            str(withdrawing)
        ])
        return output.getvalue()


class UserReportGenerator(ReportGeneratorBase):
    prefix = 'user'
    reportname_format = u'用户记录 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):
        output = cStringIO.StringIO()
        writer = UnicodeWriter(output, delimiter='\t')
        writer.writerow([u'序号', u'用户姓名', u'用户手机号', u'账户余额', u'加入日期', u'邀请人姓名', u'邀请人电话'])

        users = User.objects.filter(date_joined__gte=start_time, date_joined__lt=end_time)

        for index, user in enumerate(users):
            introduced_by = IntroducedBy.objects.filter(user=user).first()
            introduced_by_name = ""
            introduced_by_phone = ""
            name = user.username
            phone = ""
            margin = 0
            if introduced_by:
                introduced_by_name = introduced_by.introduced_by.wanglibaouserprofile.name
                introduced_by_phone = introduced_by.introduced_by.wanglibaouserprofile.phone
            if hasattr(user, "wanglibaouserprofile"):
                name = user.wanglibaouserprofile.name
                phone = user.wanglibaouserprofile.phone
            if hasattr(user, "margin"):
                margin = user.margin.margin
            writer.writerow([
                str(user.id),
                name,
                phone,
                str(margin),
                timezone.localtime(user.date_joined).strftime("%Y-%m-%d %H:%M:%S"),
                introduced_by_name,
                introduced_by_phone,
            ])
        return output.getvalue()

    @classmethod
    def generate_report(cls, start_time, end_time=None):
        if end_time is None:
            end_time = start_time + timedelta(days=1)

        assert (isinstance(start_time, datetime))
        assert (isinstance(start_time, datetime))

        path = cls.get_file_path(start_time, end_time)

        content = cls.generate_report_content(start_time, end_time)

        path = storage.save(path, ContentFile(content))
        report = Report(name=cls.get_report_name(start_time, end_time))
        report.file = path
        report.content = content
        report.save()
        return report


class ClientInfoGenerator(ReportGeneratorBase):
    prefix = 'khdxx'
    reportname_format = u'客户端信息 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):
        output = cStringIO.StringIO()
        writer = UnicodeWriter(output, delimiter='\t')
        writer.writerow([u'id', u'版本', u'设备', u'网络', u'渠道', u'手机号', u'动作', u'时间'])

        clientdatas = ClientData.objects.filter(create_time__gte=start_time, create_time__lt=end_time)

        for index, clientinfo in enumerate(clientdatas):
            writer.writerow([
                str(index + 1),
                str(clientinfo.version),
                str(clientinfo.userdevice),
                str(clientinfo.network),
                str(clientinfo.channelid),
                str(clientinfo.phone),
                str(clientinfo.action),
                timezone.localtime(clientinfo.create_time).strftime("%Y-%m-%d %H:%M:%S")
            ])
            return output.getvalue()


class ReportGenerator(object):
    @classmethod
    def generate_reports(cls, start_time, end_time=None):
        DepositReportGenerator.generate_report(start_time=start_time, end_time=end_time)
        WithDrawReportGenerator.generate_report(start_time=start_time, end_time=end_time)
        PaybackReportGenerator.generate_report(start_time=start_time, end_time=end_time)
        P2PAuditReportGenerator.generate_report(start_time=start_time, end_time=end_time)
        ProductionAmortizationsReportGenerator.generate_report(start_time=start_time, end_time=end_time)
        MarginReportGenerator.generate_report(start_time=start_time, end_time=end_time)


class RedpackReportGenerator(ReportGeneratorBase):
    prefix = 'hbls'
    reportname_format = u'红包流水 %s--%s'

    @classmethod
    def generate_report_content(cls, start_time, end_time):

        redpackrecord = RedPackRecord.objects.filter(created_at__gte=start_time, created_at__lt=end_time).\
            prefetch_related('redpack').prefetch_related('redpack__event').\
            prefetch_related('user').prefetch_related('user__wanglibaouserprofile')

        output = cStringIO.StringIO()

        writer = UnicodeWriter(output, delimiter='\t')
        writer.writerow([u'序号', u'红包活动ID', u'红包活动名称', u'用户名称', u'用户手机号', u'兑换平台', u'使用平台',
                         u'红包创建时间', u'红包使用时间', u'使用金额', u'关联订单'])
        name = ''
        phone = ''
        for index, record in enumerate(redpackrecord):
            if record.user:
                name = record.user.wanglibaouserprofile.name
                phone = record.user.wanglibaouserprofile.phone
            writer.writerow([
                str(index + 1),
                unicode(record.redpack.event.id),
                record.redpack.event.name,
                name,
                phone,
                record.change_platform,
                record.apply_platform,
                timezone.localtime(record.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                timezone.localtime(record.apply_at).strftime("%Y-%m-%d %H:%M:%S") if record.apply_at else '',
                record.apply_amount,
                unicode(record.order_id) if record.order_id else '',
            ])
        return output.getvalue()