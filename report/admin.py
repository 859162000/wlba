from django.contrib import admin
from report.models import Report


class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'file')
    list_display_links = ('name', 'file',)
    readonly_fields = ('content',)

admin.site.register(Report, ReportAdmin)