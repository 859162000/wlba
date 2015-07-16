#!/usr/bin/env python
# encoding: utf-8

import json

from misc.models import Misc


class MiscRecommendProduction(object):
    """ 设置推荐标 """
    KEY = 'recommend_production'

    def __init__(self, key=None):
        self.key = key or MiscRecommendProduction.KEY
        self.misc = self._init_recommend_product()

    def get_misc(self):
        return Misc.objects.filter(key=self.key).first()

    def _init_recommend_product(self):
        misc = self.get_misc()
        if not misc:
            misc = Misc()
            misc.key = self.key
            misc.value = json.dumps({self.key: []})
            misc.description = u'推荐标记录'
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

    def _change_product_list(self, products):
        value = json.loads(self.misc.value)
        value[self.key] = products
        self.misc.value = json.dumps(value)
        self.misc.save()
