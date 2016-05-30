#!/usr/bin/env python
# encoding:utf-8

import logging
from django.db.models import Sum
from django.utils import timezone
from django.core.urlresolvers import reverse

from misc.views import MiscRecommendProduction
from wanglibao_p2p.models import ProductAmortization, P2PProduct, P2PRecord
from wanglibao_redis.backend import redis_backend
from experience_gold.models import ExperienceAmortization, ExperienceEventRecord, ExperienceProduct

logger = logging.getLogger(__name__)


class RecommendProduct(object):
    """
    查询主推标和体验标
    """

    def __init__(self, user):
        self.user = user

    def get_recommend_product(self):
        product_result = dict()
        user = self.user
        is_p2p = False
        now = timezone.now()
        recommend_product_id = None
        misc = MiscRecommendProduction()
        if user and user.is_authenticated():
            # 主推标
            if P2PRecord.objects.filter(user=user).exists():
                # 存在购买记录
                recommend_product_id = misc.get_recommend_product_except_new()
                is_p2p = True
            else:
                # 查询是否投资过体验标
                if ExperienceAmortization.objects.filter(user=user).exists():
                    # 查询新手标
                    product_new = P2PProduct.objects.filter(hide=False, publish_time__lte=now,
                                                            status=u'正在招标', category=u'新手标')
                    if product_new.exists():
                        # 有新手标
                        id_rate = [{'id': q.id, 'rate': q.completion_rate} for q in product_new]
                        id_rate = sorted(id_rate, key=lambda x: x['rate'], reverse=True)
                        recommend_product_id = id_rate[0]['id']
                    else:
                        recommend_product_id = misc.get_recommend_product_except_new()

                    is_p2p = True
                else:
                    # 未投资过体验标
                    # 体验金可用余额
                    e_record = ExperienceEventRecord.objects.filter(user=user, apply=False, event__invalid=False)\
                        .filter(event__available_at__lt=now, event__unavailable_at__gt=now)\
                        .aggregate(Sum('event__amount'))
                    if e_record.get('event__amount__sum'):
                        e_amount = e_record.get('event__amount__sum')
                        if e_amount < 28888:
                            recommend_product_id = misc.get_recommend_product_except_new()
                            is_p2p = True
                    else:
                        # 没有可用的体验金
                        is_p2p = True

        if is_p2p:
            if not recommend_product_id:
                recommend_product_id = misc.get_recommend_product_id()
            product_result['res_type'] = 'p2p'
            product_result['results'] = self.get_p2p(recommend_product_id)
        else:
            # 显示体验标
            re_results = self.get_experience(user)

            # 如果没有体验标则显示p2p标
            if len(re_results[0]) == 0:
                recommend_product_id = misc.get_recommend_product_id()
                product_result['res_type'] = 'p2p'
                product_result['results'] = self.get_p2p(recommend_product_id)
            else:
                product_result['res_type'] = 'experience'
                product_result['results'] = re_results

        return product_result, recommend_product_id

    def get_experience(self, user):
        """
        获取体验标信息
        :param user:
        """
        res = list()
        now = timezone.now()
        experience_amount = 0.0
        experience_amount_default = 28888.0
        e_product = ExperienceProduct.objects.filter(isvalid=True).first()
        if user and user.is_authenticated():
            experience_record = ExperienceEventRecord.objects.filter(user=user, apply=False, event__invalid=False)\
                .filter(event__available_at__lt=now, event__unavailable_at__gt=now).aggregate(Sum('event__amount'))
            if experience_record.get('event__amount__sum'):
                experience_amount = experience_record.get('event__amount__sum')
        else:
            experience_amount = experience_amount_default

        if e_product:
            res_result = {
                'id': e_product.id,
                'product_name': e_product.name,
                'period': e_product.period,
                'expected_earning_rate': e_product.expected_earning_rate,
                'description': e_product.description,
                'url': reverse("experience_app_detail"),
                'cost_amount': 1.0,
                'total_amount': experience_amount,
            }
        else:
            res_result = {}

        res.append(res_result)
        return res

    def get_p2p(self, recommend_product_id):
        """
        获取P2P标详细信息
        :param recommend_product_id:
        """
        res = list()
        p2p_result = redis_backend().get_cache_p2p_detail(product_id=recommend_product_id)

        amortizations = ProductAmortization.objects.filter(product_id=recommend_product_id)\
            .values('term', 'principal', 'interest', 'penal_interest')

        product_amortization = [{
            'term': i.get('term'),
            'principal': float(i.get('principal')),
            'interest': float(i.get('interest')),
            'penal_interest': float(i.get('penal_interest'))
        } for i in amortizations]

        p2p_result['product_amortization'] = product_amortization
        p2p_result['warrant_company'] = {
            'name': p2p_result['warrant_company_name']
        }

        if p2p_result['activity']:
            activity = {
                "name": p2p_result['activity'].get('activity_rule_name', ''),
                "rule_amount": p2p_result['activity'].get('activity_rule_amount', 0.0),
                "rule_amount_text": p2p_result['activity'].get('activity_rule_percent_text', 0.0)
            }
        else:
            activity = {}

        publish_time = timezone.localtime(p2p_result['publish_time']).strftime("%Y-%m-%d %H:%M:%S")
        end_time = timezone.localtime(p2p_result['end_time']).strftime("%Y-%m-%d %H:%M:%S")
        p2p_result['publish_time'] = publish_time
        p2p_result['end_time'] = end_time

        if p2p_result['soldout_time']:
            soldout_time = timezone.localtime(p2p_result['soldout_time']).strftime("%Y-%m-%d %H:%M:%S")
            p2p_result['soldout_time'] = soldout_time
        else:
            p2p_result['soldout_time'] = ""
            
        if p2p_result['make_loans_time']:
            make_loans_time = timezone.localtime(p2p_result['make_loans_time']).strftime("%Y-%m-%d %H:%M:%S")
            p2p_result['make_loans_time'] = make_loans_time
        else:
            p2p_result['make_loans_time'] = ""

        del p2p_result['warrants']
        del p2p_result['warrant_company_name']
        del p2p_result['attachments']
        del p2p_result['activity']

        p2p_result['activity'] = activity

        res.append(p2p_result)

        return res


