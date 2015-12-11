# encoding:utf-8

import redis
import pickle
import datetime
from django.conf import settings
from wanglibao_banner.models import Partner
from decimal import Decimal
from django.http import Http404
from django.utils import timezone
from wanglibao_p2p.amortization_plan import get_amortization_plan
from wanglibao_p2p.models import P2PProduct, Warrant, Attachment
from misc.models import Misc
import json


class redis_backend(object):

    def __init__(self, host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB):
        try:
            self.password = settings.REDIS_PASSWORD
            self.pool = redis.ConnectionPool(host=host, port=port, db=db, password=self.password)
            self.redis = redis.Redis(connection_pool=self.pool)
            self.redis.set("test", "test")
        except:
            self.pool = None
            self.redis = None

    def _is_available(self):
        try:
            self.redis.ping()
            redis_config = Misc.objects.filter(key='redis_server').first()
            if redis_config:
                data = json.loads(redis_config.value)
                switch = data.get('switch')
                if switch == 'on':
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False

    def _exists(self, name):
        if self.redis:
            return self.redis.exists(name)
        return False

    def _set(self, key, value):
        if self.redis:
            self.redis.set(key, value)

    def _get(self, key):
        if self.redis:
            return self.redis.get(key)
        return None

    def _delete(self, key):
        if self.redis:
            self.redis.delete(key)

    def _lpush(self, key, value):
        if self.redis:
            self.redis.lpush(key, value)

    def _rpush(self, key, value):
        if self.redis:
            self.redis.rpush(key, value)

    def _lrange(self, key, start, end):
        if self.redis:
            return self.redis.lrange(key, start, end)

    def _lrem(self, key, value, count=0):
        if self.redis:
            self.redis.lrem(key, value, count)

    def get_cache_partners(self):

        if self._is_available() and self._exists('partners'):
            partners = pickle.loads(self._get('partners'))
        else:
            partners_data = Partner.objects.filter(type='partner')
            partners = [
                {'name': partner.name, 'link': partner.link, 'image': partner.image}
                for partner in partners_data
            ]
            self._set('partners', pickle.dumps(partners))

        return partners

    def get_cache_p2p_detail(self, product_id):

        if self._is_available() and self._exists('p2p_detail_{0}'.format(product_id)):
            p2p_results = pickle.loads(self._get('p2p_detail_{0}'.format(product_id)))
            return p2p_results
        else:
            p2p = P2PProduct.objects.select_related('activity').exclude(status=u'流标').exclude(status=u'录标').filter(pk=product_id, hide=False).first()
            if not p2p:
                return None

            if p2p.soldout_time:
                end_time = p2p.soldout_time
            else:
                end_time = p2p.end_time

            terms = get_amortization_plan(p2p.pay_method).generate(p2p.total_amount,
                                                                   p2p.expected_earning_rate / 100,
                                                                   datetime.datetime.now(),
                                                                   p2p.period)
            total_earning = terms.get("total") - p2p.total_amount
            total_fee_earning = 0

            if p2p.activity:
                total_fee_earning = Decimal(
                    p2p.total_amount * p2p.activity.rule.rule_amount * (Decimal(p2p.period) / Decimal(12)))\
                    .quantize(Decimal('0.01'))

            if p2p.types:
                types_id = p2p.types.id
                types_name = p2p.types.name
            else:
                types_id = 0
                types_name = ''

            p2p_results = {
                "id": p2p.id,
                "version": p2p.version,
                "category": p2p.category,
                "types_id": types_id,
                "types_name": types_name,
                "hide": p2p.hide,
                "name": p2p.name,
                "short_name": p2p.short_name,
                "serial_number": p2p.serial_number,
                "contract_serial_number": p2p.contract_serial_number,
                "status": p2p.status,
                "priority": p2p.priority,
                "period": p2p.period,
                "brief": p2p.brief,
                "expected_earning_rate": p2p.expected_earning_rate,
                "excess_earning_rate": p2p.excess_earning_rate,
                "excess_earning_description": p2p.excess_earning_description,
                "pay_method": p2p.pay_method,
                "display_payback_method": p2p.display_payback_method,
                "amortization_count": p2p.amortization_count,
                "repaying_source": p2p.repaying_source,
                "baoli_original_contract_number": p2p.baoli_original_contract_number,
                "baoli_original_contract_name": p2p.baoli_original_contract_name,
                "baoli_trade_relation": p2p.baoli_trade_relation,
                "borrower_name": p2p.borrower_name,
                "borrower_phone": p2p.borrower_phone,
                "borrower_address": p2p.borrower_address,
                "borrower_id_number": p2p.borrower_id_number,
                "borrower_bankcard": p2p.borrower_bankcard,
                "borrower_bankcard_bank_name": p2p.borrower_bankcard_bank_name,
                "borrower_bankcard_bank_code": p2p.borrower_bankcard_bank_code,
                "borrower_bankcard_bank_province": p2p.borrower_bankcard_bank_province,
                "borrower_bankcard_bank_city": p2p.borrower_bankcard_bank_city,
                "borrower_bankcard_bank_branch": p2p.borrower_bankcard_bank_branch,
                "total_amount": p2p.total_amount,
                "ordered_amount": p2p.ordered_amount,
                #"extra_data": json.loads(json.dumps(p2p.extra_data)),
                "publish_time": p2p.publish_time,
                "end_time": end_time,
                "soldout_time": p2p.soldout_time,
                "make_loans_time": p2p.make_loans_time,
                "limit_per_user": p2p.limit_per_user,
                "warrant_company_name": p2p.warrant_company.name,
                "usage": p2p.usage,
                "short_usage": p2p.short_usage,
                "display_status": p2p.display_status,
                "activity": {
                    "activity_name": p2p.activity.name,
                    "activity_description": p2p.activity.description,
                    "activity_rule_name": p2p.activity.rule.name,
                    "activity_rule_description": p2p.activity.rule.description,
                    "activity_rule_type": p2p.activity.rule.rule_type,
                    "activity_rule_amount": p2p.activity.rule.rule_amount,
                    "activity_rule_percent_text": p2p.activity.rule.percent_text,
                } if p2p.activity else {},
                "attachments": Attachment.objects.filter(product=p2p).values(),
                "warrants": Warrant.objects.filter(product=p2p).values(),
                "remain": p2p.remain,
                "completion_rate": p2p.completion_rate,
                "limit_amount_per_user": p2p.limit_amount_per_user,
                "current_limit": p2p.current_limit,
                "available_amount": p2p.available_amount,
                'total_earning': total_earning,
                'total_fee_earning': total_fee_earning,
                "is_taojin": p2p.is_taojin,
                "is_app_exclusive": p2p.is_app_exclusive,
            }
            extra_data = p2p.extra_data

            if extra_data:
                for section_key in extra_data:
                    for item_key in extra_data[section_key]:
                        if not item_key:
                            extra_data[section_key][section_key] = extra_data[section_key][item_key]
                            del extra_data[section_key][item_key]
            p2p_results['extra_data'] = extra_data

            if p2p.status != u'正在招标':
                self._set('p2p_detail_{0}'.format(product_id), pickle.dumps(p2p_results))

            return p2p_results

    def get_p2p_by_id(self, product_id):
        p2p = P2PProduct.objects.select_related('activity').exclude(status=u'流标') \
            .exclude(status=u'录标').filter(pk=product_id, hide=False).first()

        if p2p:
            return p2p
        else:
            return None

    def get_list_by_p2p(self, product):
        if product:
            p2p = self.get_p2p_by_id(product.id)

            if p2p.types:
                types_id = p2p.types.id
                types_name = p2p.types.name
            else:
                types_id = 0
                types_name = ''

            p2p_dict = {
                "id": p2p.id,
                "category": p2p.category,
                "types_id": types_id,
                "types_name": types_name,
                "hide": p2p.hide,
                "name": p2p.name,
                "short_name": p2p.short_name,
                "serial_number": p2p.serial_number,
                "contract_serial_number": p2p.contract_serial_number,
                "status": p2p.status,
                "priority": p2p.priority,
                "period": p2p.period,
                "brief": p2p.brief,
                "expected_earning_rate": p2p.expected_earning_rate,
                "excess_earning_rate": p2p.excess_earning_rate,
                "excess_earning_description": p2p.excess_earning_description,
                "pay_method": p2p.pay_method,
                "amortization_count": p2p.amortization_count,
                "repaying_source": p2p.repaying_source,
                "total_amount": p2p.total_amount,
                "ordered_amount": p2p.ordered_amount,
                "publish_time": p2p.publish_time,
                "end_time": p2p.soldout_time if p2p.soldout_time else p2p.end_time,
                "soldout_time": p2p.soldout_time,
                "make_loans_time": p2p.make_loans_time,
                "limit_per_user": p2p.limit_per_user,
                "warrant_company_name": p2p.warrant_company.name,
                "usage": p2p.usage,
                "short_usage": p2p.short_usage,
                "display_status": p2p.display_status,
                "display_payback_method": p2p.display_payback_method,
                "activity": {
                    "activity_name": p2p.activity.name,
                    "activity_description": p2p.activity.description,
                    "activity_rule_name": p2p.activity.rule.name,
                    "activity_rule_description": p2p.activity.rule.description,
                    "activity_rule_type": p2p.activity.rule.rule_type,
                    "activity_rule_amount": p2p.activity.rule.rule_amount,
                    "activity_rule_percent_text": p2p.activity.rule.percent_text,
                } if p2p.activity else {},
                "remain": p2p.remain,
                "completion_rate": p2p.completion_rate,
                "limit_amount_per_user": p2p.limit_amount_per_user,
                "current_limit": p2p.current_limit,
                "available_amount": p2p.available_amount,
                "is_taojin": p2p.is_taojin,
                "is_app_exclusive": p2p.is_app_exclusive,
            }
        else:
            p2p_dict = {}

        return p2p_dict

    def get_p2p_list_from_objects(self, p2p_products):

        if not p2p_products:
            return []

        p2p_list = [
            {
                "id": p2p.id,
                "category": p2p.category,
                "types_id": p2p.types.id if p2p.types else 0,
                "types_name": p2p.types.name if p2p.types else '',
                "hide": p2p.hide,
                "name": p2p.name,
                "short_name": p2p.short_name,
                "serial_number": p2p.serial_number,
                "contract_serial_number": p2p.contract_serial_number,
                "status": p2p.status,
                "priority": p2p.priority,
                "period": p2p.period,
                "brief": p2p.brief,
                "expected_earning_rate": p2p.expected_earning_rate,
                "excess_earning_rate": p2p.excess_earning_rate,
                "excess_earning_description": p2p.excess_earning_description,
                "pay_method": p2p.pay_method,
                "amortization_count": p2p.amortization_count,
                "repaying_source": p2p.repaying_source,
                "total_amount": p2p.total_amount,
                "ordered_amount": p2p.ordered_amount,
                "publish_time": p2p.publish_time,
                "end_time": p2p.soldout_time if p2p.soldout_time else p2p.end_time,
                "soldout_time": p2p.soldout_time,
                "make_loans_time": p2p.make_loans_time,
                "limit_per_user": p2p.limit_per_user,
                "warrant_company_name": p2p.warrant_company.name,
                "usage": p2p.usage,
                "short_usage": p2p.short_usage,
                "display_status": p2p.display_status,
                "display_payback_method": p2p.display_payback_method,
                "activity": {
                    "activity_name": p2p.activity.name,
                    "activity_description": p2p.activity.description,
                    "activity_rule_name": p2p.activity.rule.name,
                    "activity_rule_description": p2p.activity.rule.description,
                    "activity_rule_type": p2p.activity.rule.rule_type,
                    "activity_rule_amount": p2p.activity.rule.rule_amount,
                    "activity_rule_percent_text": p2p.activity.rule.percent_text,
                } if p2p.activity else {},
                "remain": p2p.remain,
                "completion_rate": p2p.completion_rate,
                "limit_amount_per_user": p2p.limit_amount_per_user,
                "current_limit": p2p.current_limit,
                "available_amount": p2p.available_amount,
                "is_taojin": p2p.is_taojin,
                "is_app_exclusive": p2p.is_app_exclusive,
            } for p2p in p2p_products
        ]

        return p2p_list

    # Add by hb on 2015-12-08
    def get_p2p_list_from_objects_by_status(self, p2p_products, status_int):

        if not p2p_products:
            return []

        p2p_list = [
            {
                "id": p2p.id,
                "category": p2p.category,
                "types_id": p2p.types.id if p2p.types else 0,
                "types_name": p2p.types.name if p2p.types else '',
                "hide": p2p.hide,
                "name": p2p.name,
                "short_name": p2p.short_name,
                "serial_number": p2p.serial_number,
                "contract_serial_number": p2p.contract_serial_number,
                "status": p2p.status,
                "priority": p2p.priority,
                "period": p2p.period,
                "brief": p2p.brief,
                "expected_earning_rate": p2p.expected_earning_rate,
                "excess_earning_rate": p2p.excess_earning_rate,
                "excess_earning_description": p2p.excess_earning_description,
                "pay_method": p2p.pay_method,
                "amortization_count": p2p.amortization_count,
                "repaying_source": p2p.repaying_source,
                "total_amount": p2p.total_amount,
                "ordered_amount": p2p.ordered_amount,
                "publish_time": p2p.publish_time,
                "end_time": p2p.soldout_time if p2p.soldout_time else p2p.end_time,
                "soldout_time": p2p.soldout_time,
                "make_loans_time": p2p.make_loans_time,
                "limit_per_user": p2p.limit_per_user,
                "warrant_company_name": p2p.warrant_company.name,
                "usage": p2p.usage,
                "short_usage": p2p.short_usage,
                "display_status": p2p.display_status,
                "display_payback_method": p2p.display_payback_method,
                "activity": {
                    "activity_name": p2p.activity.name,
                    "activity_description": p2p.activity.description,
                    "activity_rule_name": p2p.activity.rule.name,
                    "activity_rule_description": p2p.activity.rule.description,
                    "activity_rule_type": p2p.activity.rule.rule_type,
                    "activity_rule_amount": p2p.activity.rule.rule_amount,
                    "activity_rule_percent_text": p2p.activity.rule.percent_text,
                } if p2p.activity else {},
                "remain": p2p.remain,
                "completion_rate": p2p.completion_rate,
                "limit_amount_per_user": p2p.limit_amount_per_user,
                "current_limit": p2p.current_limit,
                "available_amount": p2p.available_amount,
                "is_taojin": p2p.is_taojin,
                "is_app_exclusive": p2p.is_app_exclusive,
            } for p2p in p2p_products if p2p.status_int==status_int
        ]

        return p2p_list

    def push_p2p_products(self, p2p):
        if p2p:
            p2p_dict = self.get_list_by_p2p(p2p)
            if p2p.status == u'还款中':
                # 将还款中的标写入redis
                self._lpush('p2p_products_repayment', pickle.dumps(p2p_dict))
            elif p2p.status == u'已完成':
                # 将已完成的标写入redis
                self._lpush('p2p_products_finished', pickle.dumps(p2p_dict))
            else:
                # 将满标状态的标写入redis
                self._lpush('p2p_products_full', pickle.dumps(p2p_dict))

        return True

    def update_detail_cache(self, product_id):
        if self._exists('p2p_detail_{0}'.format(product_id)):
            self._delete('p2p_detail_{0}'.format(product_id))

        self.get_cache_p2p_detail(product_id)

    def update_list_cache(self, source_key, target_key, product):
        if self._exists(source_key) and self._exists(target_key):
            source_cache_list = self._lrange(source_key, 0, -1)
            for source in source_cache_list:
                source_product = pickle.loads(source)
                if source_product.get('id') == product.id:
                    # 删除 source_key 中的元素
                    self._lrem(source_key, source)
                    # 将删除的元素更新后 push 进 target_key 的列表中
                    p2p_dict = self.get_list_by_p2p(product)
                    self._lpush(target_key, pickle.dumps(p2p_dict))
                    break

        return True

    def get_announcement(self):
        res = self._get('announcement')
        if not res:
            return None
        return pickle.loads(res)

    def get_news(self):
        res = self._get('announcement_news')
        if not res:
            return None
        return pickle.loads(res)

    def get_banners(self):
        res = self._get('banners')
        if not res:
            return None
        arr = pickle.loads(res)
        for x in arr[::-1]:
            if not x['start_at'] <= timezone.now() <= x['end_at']:
                arr.remove(x)
        return arr
