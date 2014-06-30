#encoding: utf8
from django.contrib.auth import get_user_model
from wanglibao_pay.models import Bank, Card


class PayMockGenerator(object):
    @classmethod
    def generate_bank(cls, clean=False):
        if clean:
            Bank.objects.all().delete()

        banks = [
            (u'兴业银行', '09', 'xyyh', 'CIB'),
            (u'民生银行', '12', 'msyh', 'CMBC'),
            (u'华夏银行', '13', 'hxyh', 'HXB'),
            (u'北京银行', '15', 'bjyh', 'BCCB'),
            (u'浦发银行', '16', 'pfyh', 'SPDB'),
            (u'广发银行', '19', 'gfyh', 'GDB'),
            (u'交通银行', '21', 'jtyh', 'BOCOM'),
            (u'工商银行', '25', 'gsyh', 'ICBC'),
            (u'中国建设银行', '27', 'jsyh', 'CCB'),
            (u'招商银行', '28', 'zsyh', 'CMB'),
            (u'中国农业银行', '29', 'nyyh', 'ABC'),
            (u'中信银行', '33', 'zxyh', 'CITIC'),
            (u'光大银行', '36', 'gdyh', 'CEB'),
            (u'北京农商银行', '40', 'bjnsyh', 'BJRCB'),
            (u'中国银行', '45', 'zgyh', 'BOC'),
            (u'中国邮政储蓄银行', '46', 'yzyh', 'PSBC'),
            (u'南京银行', '49', 'njyh', 'NJCB'),
            (u'平安银行', '50', 'payh', 'PINGAN'),
            (u'杭州银行', '51', 'hzyh', 'HZCB'),
            (u'浙商银行', '53', 'zhesyh', 'CZB'),
            (u'上海银行', '54', 'shyh', 'BOS'),
            (u'渤海银行', '55', 'bhyh', 'CBHB'),
            (u'东亚银行', '', 'dyyh', 'HKBEA'),
            (u'深发银行', '', 'sfyh', 'SDB'),
        ]

        for name, gate_id, logo, code in banks:
            bank = Bank()
            bank.name = name
            bank.gate_id = gate_id
            bank.code = code
            bank.logo = '/static/images/bank-logos/' + logo + '.png'
            bank.limit = u"""
                <table>
                  <thead>
                    <tr>
                      <th rowspan="2">卡种</th>
                      <th colspan="2">专业版(签约客户)</th>
                      <th colspan="2">大众版(非签约客户)</th>
                    </tr>
                    <tr>
                      <th>单笔限额</th>
                      <th>每日限额</th>
                      <th>单笔限额</th>
                      <th>每日限额</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>借记卡</td>
                      <td>客户自行设定</td>
                      <td>客户自行设定</td>
                      <td>500</td>
                      <td>500</td>
                    </tr>
                    <tr>
                      <td>信用卡</td>
                      <td colspan="4">不支持</td>
                    </tr>
                  </tbody>
                </table>
"""
            bank.save()

    @classmethod
    def generate_card(cls, clean=False):
        if clean:
            Card.objects.all().delete()

        banks = Bank.objects.all()
        users = get_user_model().objects.all()

        for user in users:
            for bank in banks:
                card = Card()
                card.bank = bank
                card.user = user
                card.no = '6228480402564890018'
                card.save()