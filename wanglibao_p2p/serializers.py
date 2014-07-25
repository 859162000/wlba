# coding=utf-8
import json
from wanglibao.serializers import ModelSerializerExtended
from rest_framework import serializers
from wanglibao_p2p.models import P2PProduct, P2PRecord


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
    class Meta:
        model = P2PProduct
        depth = 1
        exclude = ('contract_template', 'bought_people_count', 'bought_count', 'bought_amount', 'bought_count_random', 'bought_amount_random', 'version')

    def transform_extra_data(self, obj, value):
        extra_data = json.loads(value)

        if not self.request.user.is_authenticated():
            for section_key in extra_data:
                for item_key in extra_data[section_key]:
                    extra_data[section_key][item_key] = u'请登录后查看'

        return json.dumps(extra_data, ensure_ascii=False)
