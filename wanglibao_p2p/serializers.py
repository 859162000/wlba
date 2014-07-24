# coding=utf-8
import json
from wanglibao.serializers import ModelSerializerExtended
from wanglibao_p2p.models import P2PProduct


class P2PProductSerializer(ModelSerializerExtended):

    class Meta:
        model = P2PProduct
        depth = 1
        exclude = ('contract_template',)

    def transform_extra_data(self, obj, value):
        extra_data = json.loads(value)

        if not self.request.user.is_authenticated():
            for section_key in extra_data:
                for item_key in extra_data[section_key]:
                    extra_data[section_key][item_key] = u'请登录后查看'

        return json.dumps(extra_data, ensure_ascii=False)
