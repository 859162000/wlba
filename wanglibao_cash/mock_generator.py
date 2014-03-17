# encoding: utf-8
import random
import datetime

from wanglibao_cash.models import CashIssuer, Cash


class MockGenerator(object):

    @classmethod
    def generate_cash_issuers(cls, clean=False):
        if clean:
            [item.delete() for item in CashIssuer.objects.iterator()]

        for index in range(0, 100):
            issuer = CashIssuer()
            issuer.name = u'发行机构' + str(index + 1)
            issuer.description = u'国内第%d家发行机构' % (index + 1, )
            issuer.home_page = 'http://www.example.com'
            issuer.phone = '95555'
            issuer.save()

    @classmethod
    def generate_cashes(cls, clean=False):
        if clean:
            for cash in Cash.objects.all():
                cash.delete()

        issuers = CashIssuer.objects.all()
        issuer_count = len(issuers)

        for index in range(0, 1000):
            cash = Cash()

            cash.name = u'现金类理财' + str(index + 1)
            cash.status = (u'开放', u'关闭')[random.randrange(0,2)]
            cash.issuer = issuers.get(pk=random.randrange(1, issuer_count))
            cash.period = random.randrange(0, 48)

            cash.profit_10000 = random.randrange(0, 10) / 5.0
            cash.profit_rate_7days = random.randrange(0, 10)

            cash.buy_url = 'http://www.example.com'
            cash.buy_text = cash.name

            cash.brief = u'难得一见的现金类理财产品 快抢'
            cash.buy_brief = u"""余额宝转入有金额限制吗？
用余额转入余额宝无额度限制，用借记卡快捷转入余额宝不同银行额度不同,以收银台提示限额为准。

我可以用借记卡网银方式给余额宝转钱吗？
不支持，请先开通借记卡快捷，或者用网银充值到余额，再用余额转入余额宝。

可以设置自动转入余额宝吗？
可以，请见自动转入余额宝开通流程"""
            cash.redeem_brief = u"""转出到支付宝余额有额度限制吗？
电脑端证书用户：单笔5万元，单日5万元，单月20万元；非证书用户：单笔2万元，单日2万元，单月20万元；
无线端：单笔5万元，单日5万元，单月20万元；
温馨提醒：余额宝转出至支付宝余额和余额宝消费共享额度。

余额宝转出至银行卡有次数和额度限制吗？
一个账户一天最多可操作3次转出至银行卡。限额如下：1、转出到储蓄卡快捷：单笔/日累计100万元；2、转出到普通提现卡：单笔单日15万元；3、实时提现的额度：中信（柜台签约：最高1万元/笔/日；个人网银签约：最高5000元/笔/日（文件证书）、1万元/笔/日（移动证书）；个人网银无证书用户发起签约：最高200元/笔/日）、光大（最高5000元/笔/日）、平安（最高5000元/笔/日）、招行（最高5万元/笔/日）

余额宝转出至银行卡到账时间？
单笔5万元以下（含5万），第二个自然日24点前到账，如10月1日操作，请在10月2日关注到账情况；单笔高于5万元，提交后的一个工作日内24点前到账；实时到账：仅支持中信、光大、平安、招行卡通；2小时到账：仅支持无线，日累计5万以内（含），且在该卡服务时间内
温馨提示：工作日是不包括国定节假日、周末。自然日不区分周末及国定节假日。

余额宝消费和转出当天有收益吗？
购物消费支付和转出的部分，当天是没有收益的"""
            cash.profit_brief = u"""什么时候能看到收益到账？
转入资金在基金公司确认份额的第2天可以看到收益.
*如遇国家法定假期，基金公司不进行份额确认，以实际收益时间为准。

每天的收益是怎么计算的？
当日收益=（余额宝已确认份额的资金/10000 ）X 每万份收益。假设您已确认份额的资金为9000元，当天的每万份收益为1.25元，代入计算公式，您当日的收益为：1.13元。

余额宝的收益结算有什么规则？
余额宝的收益每日结算，每天下午15:00左右前一天的收益到账。您用余额宝消费或转出的那部分资金，当天没有收益。"""
            cash.safe_brief = u'难得一见的现金类理财产品 快抢'

            cash.save()


