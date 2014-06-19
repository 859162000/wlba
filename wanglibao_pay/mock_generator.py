#encoding: utf8
from django.contrib.auth import get_user_model
from wanglibao_pay.models import Bank, Card


class PayMockGenerator(object):
    @classmethod
    def generate_bank(cls, clean=False):
        if clean:
            Bank.objects.all().delete()

        banks = [
            (u'工商银行', '09', 'gsyh', 'ICBC'),
            (u'中国农业银行', '01', 'nyyh', ''),
            (u'招商银行', '01', 'zsyh', 'CMB'),
            (u'交通银行', '01', 'jtyh', 'BOCOM'),
            (u'中国邮政储蓄银行', '01', 'yzyh', ''),
            (u'广发银行', '01', 'gfyh', ''),
            (u'中国建设银行', '01', 'jsyh', 'CCB'),
            (u'中国银行', '01', 'zgyh', ''),
            (u'浦发银行', '01', 'pfyh', ''),
            (u'中信银行', '01', 'zxyh', ''),
            (u'华夏银行', '01', 'hxyh', ''),
            (u'兴业银行', '01', 'xyyh', 'CIB'),
            (u'平安银行', '01', 'payh', '')
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