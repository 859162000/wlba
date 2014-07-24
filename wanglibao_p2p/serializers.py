from rest_framework import serializers
from wanglibao_p2p.models import P2PProduct, WarrantCompany


class P2PProductSerializer(serializers.ModelSerializer):

    def __init__(self, request=None, *args, **kwargs):
        super(P2PProductSerializer, self).__init__(*args, **kwargs)
        self.request = request

    class Meta:
        model = P2PProduct
        depth = 1
        exclude = ('contract_template',)
