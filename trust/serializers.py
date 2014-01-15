from rest_framework.serializers import ModelSerializer
from models import Trust, Issuer


class IssuerSerializer(ModelSerializer):
    class Meta:
        model = Issuer

