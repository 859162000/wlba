# coding=utf-8
from datetime import timedelta, datetime
from os.path import join
from os import makedirs
import csv
import codecs
import cStringIO
import logging
import binascii,os
import base64
from django.conf import settings

from report.models import Report
from wanglibao_p2p.models import UserAmortization, P2PProduct
from wanglibao_pay.models import PayInfo
from M2Crypto import RSA,BIO,EVP



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
                    payinfo.user.wanglibaouserprofile.phone,
                    str(payinfo.order.id),
                    u'线上充值',
                    unicode(payinfo.bank.name),
                    str(payinfo.amount),
                    str(payinfo.fee),
                    str(payinfo.amount - payinfo.fee),
                    unicode(payinfo.status),
                    payinfo.create_time.strftime("%Y-%m-%d %H:%M"),
                    str(payinfo.request_ip),
                ])

            report = Report(name=u'充值记录 %s' % start_time.strftime('%Y-%m-%d %H:%M:%S'))
            report.file = join('reports', 'czjl', filename)
            report.save()
            tsv_file.close()
            cls.encryptFile(path)
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
            tsv_file.close()
            cls.encryptFile(path)
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
            tsv_file.close()
            cls.encryptFile(path)
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

            report = Report(name=u'满标复审 %s' % start_time.strftime('%Y-%m-%d %H:%M:%S'))
            report.file = join('reports', fileprefix, filename)
            report.save()
            tsv_file.close()
            cls.encryptFile(path)
            return report



    @classmethod
    def encryptFile(cls, path):
        file = open(path,"r+")
        rsa = Rsa()
        ase = Aes()
        all_text = file.read()
        crypt_key = binascii.b2a_hex(os.urandom(15))
        encrypt_text = ase.encrypt(crypt_key, all_text)
        encrypt_key = base64.b64encode(rsa.encrypt(crypt_key))
        file.seek(0)
        file.write(encrypt_key)
        file.write('\n')
        file.write(encrypt_text)
        file.close()
    @classmethod
    def decryptFile(cls, path):
        file = open(path, 'r')
        rsa = Rsa()
        ase = Aes()
        all_line = file.readlines()
        all_key = base64.decodestring(all_line[0].strip('\n'))
        all_text = all_line[1].strip('\n')
        print(all_text)
        decrypt_key = rsa.decrypt(all_key)
        print(decrypt_key)
        decrypt_text = ase.decrypt(decrypt_key, all_text)
        print(decrypt_text)


class Rsa:
    def genRsaKeyPair(self, rsalen=1024):
        try:
            rsa_key = RSA.gen_key(rsalen, 3, lambda *args:None)
            rsa_key.save_key("pri_key.pem", None)
            rsa_key.save_pub_key("pub_key.pem")
        except OSError, e:
            if e.errno != 17:
                raise

    def encrypt(self, data):
        try:
            pub_key = RSA.load_pub_key("pub_key.pem")
        except OSError, e:
            if e.errno != 17:
                raise
        return pub_key.public_encrypt(data, RSA.pkcs1_oaep_padding)

    def decrypt(self, data):
        try:
            string = open("pri_key.pem", "rb").read()
        except OSError, e:
            if e.errno != 17:
                raise
        bio = BIO.MemoryBuffer(string)
        pri_key = RSA.load_key_bio(bio)
        return pri_key.private_decrypt(data, RSA.pkcs1_oaep_padding)

class Aes:
    def get_cryptor(self, op, key, alg='aes_128_ecb', iv=None):
        if iv == None:
            iv = '\0' * 16
        cryptor = EVP.Cipher(alg=alg, key=key, iv=iv, op=op)
        return cryptor

    def encrypt(self, key, plaintext):
        cryptor = self.get_cryptor(1, key)
        ret = cryptor.update(plaintext)
        ret = ret + cryptor.final()
        ret = binascii.hexlify(ret)
        return ret

    def decrypt(self, key, ciphertext):
        cryptor = self.get_cryptor(0, key)
        ciphertext = binascii.unhexlify(ciphertext)
        ret = cryptor.update(ciphertext)
        ret = ret + cryptor.final()
        return ret
