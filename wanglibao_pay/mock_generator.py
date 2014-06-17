#encoding: utf8
from pinyin import pinyin
from wanglibao_pay.models import Bank


class MockGenerator(object):
    @classmethod
    def generate_bank(cls, clean=False):
        if clean:
            Bank.objects.all().delete()

        banks = [
            (u'工商银行', '09', 'gsyh'),
            (u'中国农业银行', '01', 'nyyh'),
            (u'招商银行', '01', 'zsyh'),
            (u'交通银行', '01', 'jtyh'),
            (u'中国邮政储蓄银行', '01', 'yzyh'),
            (u'广发银行', '01', 'gfyh'),
            (u'中国建设银行', '01', 'jsyh'),
            (u'中国银行', '01', 'zgyh'),
            (u'浦发银行', '01', 'pfyh'),
            (u'中信银行', '01', 'zxyh'),
            (u'华夏银行', '01', 'hxyh'),
            (u'平安银行', '01', 'payh')
        ]

        for name, gate_id, logo in banks:
            bank = Bank()
            bank.name = name
            bank.gate_id = gate_id
            bank.code = pinyin.get_initial(name).upper()
            bank.logo = '/static/images/bank-logos/'+ logo + '.png'
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

