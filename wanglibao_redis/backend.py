# encoding:utf-8

import redis
import pickle
import datetime
# from django.core.cache import cache
from wanglibao_banner.models import Partner
from decimal import Decimal
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.db.models import Q, Sum
from wanglibao_p2p.amortization_plan import get_amortization_plan
from wanglibao_p2p.models import P2PProduct, P2PEquity, ProductAmortization, Warrant, UserAmortization, \
    P2PProductContract, InterestPrecisionBalance, Attachment
# from wanglibao_p2p.forms import PurchaseForm, BillForm
import json


class redis_backend(object):

    def __init__(self, host='localhost', port=6379, db=0):
        self.pool = redis.ConnectionPool(host=host, port=port, db=db)
        self.redis = redis.Redis(connection_pool=self.pool)

    def get_cache_partners(self):

        if self.redis.exists('partners'):
            partners = pickle.loads(self.redis.get('partners'))
        else:
            partners_data = Partner.objects.filter(type='partner')
            partners = [
                {'name': partner.name, 'link': partner.link, 'image': partner.image}
                for partner in partners_data
            ]
            self.redis.set('partners', pickle.dumps(partners))

        return partners

    def get_cache_p2p_detail(self, product_id):

        if self.redis.exists('p2p_detail_{0}'.format(product_id)):
            p2p_results = pickle.loads(self.redis.get('p2p_detail_{0}'.format(product_id)))
            return p2p_results
        else:
            try:
                p2p = P2PProduct.objects.select_related('activity')\
                    .exclude(status=u'流标').exclude(status=u'录标').get(pk=product_id, hide=False)

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

                p2p_results = {
                    "id": p2p.id,
                    "version": p2p.version,
                    "category": p2p.category,
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
                    "extra_data": json.loads(json.dumps(p2p.extra_data)),
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
                    "available_amount": p2p.available_amout,
                    'total_earning': total_earning,
                    'total_fee_earning': total_fee_earning,
                }

                if p2p.status != u'正在招标':
                    self.redis.set('p2p_detail_{0}'.format(product_id), pickle.dumps(p2p_results))

            except P2PProduct.DoesNotExist:
                raise Http404(u'您查找的产品不存在')

            return p2p_results

    def get_p2p_cache_list(self):
        if self.redis.exists('p2p_products'):
            p2p_products = pickle.loads(self.redis.get('p2p_products'))
            return p2p_products
        else:

            return ""

    def get_p2p_list_from_objects(self, p2p_products):

        if not p2p_products:
            return []

        p2p_list = [
            {
                "id": p2p.id,
                "category": p2p.category,
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
                "available_amount": p2p.available_amout,
            } for p2p in p2p_products
        ]

        return p2p_list
