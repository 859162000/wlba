#!/usr/bin/env python
# encoding: utf-8

import json

from django.db.models import Q
from misc.models import Misc, timestamp
from wanglibao_p2p.models import P2PProduct


class MiscRecommendProduction(object):
    """ 设置推荐标 """
    KEY = 'recommend_production'
    DESCRIPTION = u'推荐标记录'

    KEY_PC_DATA = 'pc_index_data'
    DESC_PC_DATA = u'pc网站首页统计数据'

    KEY_INCOME_DATA = 'app_income_data'
    DESC_INCOME_DATA = u'app端收益比例参数'

    def __init__(self, key=None, desc=None, data=None):
        self.key = key or MiscRecommendProduction.KEY
        self.description = desc or MiscRecommendProduction.DESCRIPTION
        self.data = data or []
        self.misc = self._init_recommend_product()

    def get_misc(self):
        return Misc.objects.filter(key=self.key).first()

    def _init_recommend_product(self):
        misc = self.get_misc()
        if not misc:
            misc = Misc()
            misc.key = self.key
            misc.value = json.dumps({self.key: self.data})
            misc.description = self.description
            misc.save()
        return misc

    def get_recommend_products(self):
        value = json.loads(self.misc.value)
        return value[self.key]

    def add_product(self, product_id):
        id_list = self.get_recommend_products()
        if product_id not in id_list:
            id_list.append(product_id)
            self._change_product_list(products=id_list)
            return True
        return False

    def del_product(self, product_id):
        id_list = self.get_recommend_products()
        if product_id in id_list:
            id_list.remove(product_id)
            self._change_product_list(products=id_list)
            return True
        return False

    def update_value(self, value):
        if value:
            Misc.objects.filter(key=self.key).update(value=json.dumps({self.key: value}), updated_at=timestamp())
            return True
        return False

    def _change_product_list(self, products):
        value = json.loads(self.misc.value)
        value[self.key] = products
        self.misc.value = json.dumps(value)
        self.misc.save()

    def get_recommend_product_id(self):
        """ 根据业务规则获取一个推荐标的
        如果没有设置推荐标的，则根据业务规则展示一个正在招标的标id
        """
        ids = self.get_recommend_products()
        if ids:
            for id in ids:
                recommend = P2PProduct.objects.filter(hide=False, status=u'正在招标', id=id)
                if recommend:
                    return id
        # 自定义查询标
        productions = P2PProduct.objects.filter(hide=False, status=u'正在招标').exclude(Q(category=u'票据') | Q(category=u'酒仙众筹标'))
        if productions:
            id_rate = [{'id': q.id, 'rate': q.completion_rate} for q in productions]
            id_rate = sorted(id_rate, key=lambda x: x['rate'], reverse=True)
            return id_rate[0]['id']

        else:
            product = P2PProduct.objects.filter(hide=False).exclude(Q(category=u'票据') | Q(category=u'酒仙众筹标')).order_by('-priority', '-publish_time').first()
            return product.id