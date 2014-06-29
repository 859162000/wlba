from django.contrib import admin
from marketing.models import NewsAndReport


class NewsAndReportAdmin(admin.ModelAdmin):
    list_display = ("name", "link", "score")


admin.site.register(NewsAndReport, NewsAndReportAdmin)
