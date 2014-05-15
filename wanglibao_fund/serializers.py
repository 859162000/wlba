from rest_framework import serializers
from wanglibao_buy.serializers import AvailableFundSerializer
from wanglibao_fund.models import Fund, IssueBackEndChargeRate, IssueFrontEndChargeRate, RedeemFrontEndChargeRate, RedeemBackEndChargeRate


class ChargeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueBackEndChargeRate
        fields = [
            'bottom_line',
            'top_line',
            'line_type',
            'value',
            'value_type'
        ]


class IssueFrontEndChargeRateSerializer(ChargeRateSerializer):
    class Meta(ChargeRateSerializer.Meta):
        model = IssueFrontEndChargeRate


class IssueBackEndChargeRateSerializer(ChargeRateSerializer):
    class Meta(ChargeRateSerializer.Meta):
        model = IssueBackEndChargeRate


class RedeemFrontEndChargeRateSerializer(ChargeRateSerializer):
    class Meta(ChargeRateSerializer.Meta):
        model = RedeemFrontEndChargeRate


class RedeemBackEndChargeRateSerializer(ChargeRateSerializer):
    class Meta(ChargeRateSerializer.Meta):
        model = RedeemBackEndChargeRate


class FundSerializer(serializers.ModelSerializer):
    issue_back_end_charge_rates = IssueBackEndChargeRateSerializer(many=True)
    issue_front_end_charge_rates = IssueFrontEndChargeRateSerializer(many=True)
    redeem_front_end_charge_rates = RedeemFrontEndChargeRateSerializer(many=True)
    redeem_back_end_charge_rates = RedeemBackEndChargeRateSerializer(many=True)
    availablefund = AvailableFundSerializer()

    class Meta:
        model = Fund
        depth = 1
