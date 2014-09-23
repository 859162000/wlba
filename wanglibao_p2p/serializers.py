# coding=utf-8
import json
from wanglibao.serializers import ModelSerializerExtended
from rest_framework import serializers
from wanglibao_p2p.models import P2PProduct, P2PRecord
from wanglibao_p2p.amortization_plan import get_amortization_plan
from django.utils import timezone

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
    #总收益
    total_earning = serializers.SerializerMethodField('total_earning_joined')

    publish_time = serializers.SerializerMethodField('publish_time_format')
    end_time = serializers.SerializerMethodField('end_time_format')
    soldout_time = serializers.SerializerMethodField('soldout_time_format')
    # total_amount = serializers.SerializerMethodField('total_amount_format')
    # ordered_amount = serializers.SerializerMethodField('ordered_amount_format')
    display_status = serializers.SerializerMethodField('display_status_format')


    class Meta:
        model = P2PProduct
        depth = 1
        # exclude = ('contract_template', 'bought_people_count', 'bought_count', 'bought_amount', 'bought_count_random', 'bought_amount_random', 'version')
        fields = ("total_earning", "id", "version", "category", "hide", "name", "short_name", "serial_number",
                  "contract_serial_number", "status", "priority", "period", "brief", "expected_earning_rate",
                  "excess_earning_rate", "excess_earning_description", "pay_method", "amortization_count",
                  "repaying_source", "baoli_original_contract_number", "baoli_original_contract_name",
                  "baoli_trade_relation", "borrower_name", "borrower_phone", "borrower_address",
                  "borrower_id_number", "borrower_bankcard", "borrower_bankcard_bank_name",
                  "borrower_bankcard_bank_code", "borrower_bankcard_bank_province", "borrower_bankcard_bank_city",
                  "borrower_bankcard_bank_branch", "total_amount", "ordered_amount", "extra_data", "publish_time",
                  "end_time", "soldout_time", "limit_per_user", "warrant_company", "usage", "short_usage", "display_status")


    def total_earning_joined(self, obj):
        terms = get_amortization_plan(obj.pay_method).generate(obj.total_amount,
                                                               obj.expected_earning_rate/100,
                                                               obj.amortization_count,
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

    # def total_amount_format(self, obj):
    #     return float(obj.total_amount) / 10000
    #
    # def ordered_amount_format(self, obj):
    #     return float(obj.total_amount) / 10000


    def display_status_format(self, obj):
        return obj.display_status

    def transform_extra_data(self, obj, value):
        if value is None:
            return value

        extra_data = json.loads(value)

        if not self.request.user.is_authenticated():
            for section_key in extra_data:
                for item_key in extra_data[section_key]:
                    extra_data[section_key][item_key] = u'请登录后查看'

        return extra_data