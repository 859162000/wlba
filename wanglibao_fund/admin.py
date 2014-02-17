from django.contrib import admin
from wanglibao_fund.models import Fund, FundIssuer, IssueFrontEndChargeRate, RedeemBackEndChargeRate, RedeemFrontEndChargeRate, IssueBackEndChargeRate

admin.site.register(Fund)
admin.site.register(IssueFrontEndChargeRate)
admin.site.register(IssueBackEndChargeRate)
admin.site.register(RedeemFrontEndChargeRate)
admin.site.register(RedeemBackEndChargeRate)
admin.site.register(FundIssuer)
