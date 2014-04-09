import codecs
import sys
import requests
from wanglibao_cash.models import Cash, CashIssuer
from wanglibao_robot.util import parse_percent


def load_items_from_file(filename, encoding="UTF-16"):
    lines = codecs.open(filename, encoding=encoding).readlines()
    header = lines[0].strip()
    content_lines = lines[1:]

    headers = header.split('\t')

    results = []
    for content_line in content_lines:
        content_fields = content_line.strip().split('\t')

        if len(content_fields) != len(headers):
            print 'Field name not synced, %d header %d field' % (len(headers), len(content_fields))
        else:
            item = {}
            for i in range(0, len(headers)):
                item[headers[i]] = content_fields[i]

            results.append(item)

    return results


def get_or_create_issuer(name):
    if CashIssuer.objects.filter(name=name).exists():
        issuer = CashIssuer.objects.get(name=name)

    else:
        issuer = CashIssuer()
        issuer.name = name
        issuer.save()

    return issuer.id


mapping = {
    'name': 'name',
    'issuer': ('issuer_id', get_or_create_issuer),
    'status': 'status',
    'period': 'period',
    'profit rate 7 days': ('profit_rate_7days', parse_percent),
    'buy url': 'buy_url',
    'buy text': 'buy_text',
    'brief': 'brief',
    'buy brief': 'buy_brief',
    'redeem brief': 'redeem_brief',
    'profit brief': 'profit_brief',
    'safe brief': 'safe_brief'
}


def load_cash_from_file(filename, encoding="UTF-16", clean=False):
    if clean:
        print 'cleaning old data'
        Cash.objects.all().delete()
        print 'cleaning done'

    items = load_items_from_file(filename, encoding=encoding)

    results = []
    for item in items:
        cash = Cash()

        for k, v in item.items():
            if k in mapping:
                if not isinstance(mapping[k], tuple):
                    field_name = mapping[k]
                else:
                    field_name, generator = mapping[k]
                    v = generator(v)

                if hasattr(cash, field_name):
                    setattr(cash, field_name, v)
                else:
                    print "field: %s not exist on object" % (field_name,)
            else:
                print 'Field %s not in mapping' % (k,)

        cash.save()
        sys.stdout.write('.')
        results.append(cash)

    return results


def scrawl_cash():
    response = requests.post('http://stock.finance.sina.com.cn/box/api/openapi.php/MoneyFinanceFundInfoService.getProfit',
                             data={'start': '2014-04-08', 'end': '2014-04-08'})

    results = []
    for item in response.json()['result']['data']:
        name = item['platform']
        if Cash.objects.filter(name=name).exists():
            cash = Cash.objects.get(name=name)
            cash.brief = item['remark']
            cash.profit_10000 = float(item['wfsy'])
            cash.profit_rate_7days = float(item['qrnh'])
            cash.buy_url = item['buy_url']

            cash.save()
            results.append(cash)

    return results
