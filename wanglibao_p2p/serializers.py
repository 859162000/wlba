# coding=utf-8
import json
from wanglibao.serializers import ModelSerializerExtended
from rest_framework import serializers
from wanglibao_p2p.models import P2PProduct, P2PRecord
from wanglibao_p2p.amortization_plan import get_amortization_plan
from django.utils import timezone
from views import P2PEquity
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


def safe_phone(phone):
    return phone[:3] + '*' * (len(phone) - 4 - 3) + phone[-4:]


class P2PRecordSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_username')

    class Meta:
        model = P2PRecord
        fields = ('amount', 'user', 'create_time')

    def get_username(self, obj):
        return safe_phone(obj.user.wanglibaouserprofile.phone)


class P2PProductSerializer(ModelSerializerExtended):
    # 总收益
    total_earning = serializers.SerializerMethodField('total_earning_joined')

    publish_time = serializers.SerializerMethodField('publish_time_format')
    end_time = serializers.SerializerMethodField('end_time_format')
    soldout_time = serializers.SerializerMethodField('soldout_time_format')
    display_status = serializers.SerializerMethodField('display_status_format')
    pay_method = serializers.SerializerMethodField('pay_method_format')

    product_amortization = serializers.SerializerMethodField('product_amortization_format')

    activity = serializers.SerializerMethodField('activity_format')

    # add by hb on 2015-08-27
    is_taojin = serializers.SerializerMethodField('is_taojin_format')

    class Meta:
        model = P2PProduct
        depth = 1
        fields = ("total_earning", "id", "version", "category", "hide", "is_app_exclusive",
                  "name", "short_name", "serial_number",
                  "contract_serial_number", "status", "priority", "period", "expected_earning_rate",
                  "excess_earning_rate", "excess_earning_description", "pay_method", "amortization_count",
                  "repaying_source", "total_amount", "ordered_amount", "extra_data", "publish_time",
                  "end_time", "soldout_time", "limit_per_user", "warrant_company", "usage", "short_usage",
                  "display_status", "is_taojin", "product_amortization", "activity")

    def total_earning_joined(self, obj):
        terms = get_amortization_plan(obj.pay_method).generate(obj.total_amount,
                                                               obj.expected_earning_rate/100,
                                                               timezone.now(),
                                                               obj.period)
        return float(terms.get("total") - obj.total_amount)

    def publish_time_format(self, obj):
        return timezone.localtime(obj.publish_time).strftime("%Y-%m-%d %H:%M:%S")

    def end_time_format(self, obj):
        return timezone.localtime(obj.end_time).strftime("%Y-%m-%d %H:%M:%S")

    def soldout_time_format(self, obj):
        if obj.soldout_time:
            return timezone.localtime(obj.soldout_time).strftime("%Y-%m-%d %H:%M:%S")
        return ""

    def display_status_format(self, obj):
        return obj.display_status

    # add by hb on 2015-08-27
    def is_taojin_format(self, obj):
        return obj.is_taojin

    def transform_extra_data(self, obj, value):
        if value is None:
            return value

        extra_data = json.loads(value, object_pairs_hook=OrderedDict)

        # is_login = True
        # if not self.request.user.is_authenticated():
        #     is_login = False
        try:
            for section_key in extra_data:
                for item_key in extra_data[section_key]:
                    # if not item_key:
                    #     if not is_login:
                    #         extra_data[section_key][section_key] = u'请登录后查看'
                    #     else:
                    #         extra_data[section_key][section_key] = extra_data[section_key][item_key]
                    #     del extra_data[section_key][item_key]
                    # else:
                    #     if not is_login:
                    #         extra_data[section_key][item_key] = u'请登录后查看'
                    print section_key, '===', item_key

                    if not item_key:
                        extra_data[section_key][section_key] = extra_data[section_key][item_key]
                        del extra_data[section_key][item_key]
                    else:
                        if item_key == u'第三方担保机构':
                            del extra_data[section_key][item_key]
        except:
            logger.error('parse extra data failed:' + str(value))

        return extra_data

    def pay_method_format(self, obj):
        pay_method = obj.display_payback_mapping.get(obj.pay_method)
        return pay_method

    def product_amortization_format(self, obj):
        amortizations = obj.amortizations.all()

        pro_amort_list = [{
                'term': i.term,
                'principal': float(i.principal),
                'interest': float(i.interest),
                'penal_interest': float(i.penal_interest)
            } for i in amortizations]

        return pro_amort_list

    def activity_format(self, obj):

        return dict(zip(('name', 'rule_amount'),
                    (obj.activity.name, float(obj.activity.rule.rule_amount)))) if obj.activity else None


class P2PEquitySerializer(ModelSerializerExtended):
    """ there noting """
    class Meta:
        model = P2PEquity
        fields = ('id', 'created_at')


class P2PProductAPISerializer(ModelSerializerExtended):
    """ there noting """
    equities = P2PEquitySerializer()

    class Meta:
        model = P2PProduct
        deep = 1
        fields = ( "id", "version", "category", "equities")

    # def p2pequity_format(self, obj):
    #     p2pequity_list = P2PEquity.objects.filter(product__id=obj.id)
    #     return  p2pequity_list


