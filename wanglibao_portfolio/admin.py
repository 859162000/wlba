from django.contrib import admin
from models import Portfolio, UserPortfolio, ProductType, PortfolioProductEntry


class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'risk_score', 'asset_min', 'asset_max', 'expected_earning_rate', 'products')
    fieldsets = (
        (None, {
            "fields":(('name', 'description'),
                      ('risk_score', 'asset_min', 'asset_max', 'expected_earning_rate'),
                     )
        }),
    )

admin.site.register(ProductType)
admin.site.register(Portfolio)
admin.site.register(UserPortfolio)
admin.site.register(PortfolioProductEntry)
