# encoding:utf-8
from django.contrib import admin
from report.models import Report
from report.views import AdminReportExport

class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'file')
    list_display_links = ('name', 'file',)
    readonly_fields = ('content',)

admin.site.register(Report, ReportAdmin)
admin.site.register_view('report/export', view=AdminReportExport.as_view(),name=u'自定义导出表格')