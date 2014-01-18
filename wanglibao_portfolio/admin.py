from django.contrib import admin
from models import Portfolio, UserPortfolio


class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'risk_score', 'asset_min', 'asset_max', 'expected_earning_rate', 'cash', 'stock', 'p2p')
    fieldsets = (
        (None, {
            "fields":(('name', 'description'),
                      ('risk_score', 'asset_min', 'asset_max', 'expected_earning_rate'),
                      ('cash', 'stock', 'p2p'))
        }),
    )

admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(UserPortfolio)
