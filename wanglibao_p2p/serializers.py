from wanglibao.serializers import ModelSerializerExtended
from wanglibao_p2p.models import P2PProduct


class P2PProductSerializer(ModelSerializerExtended):

    class Meta:
        model = P2PProduct
        depth = 1
        exclude = ('contract_template',)
