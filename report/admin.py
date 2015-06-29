# encoding:utf-8
from django.contrib import admin
from report.models import Report
from report.views import AdminReportExport

class ReportAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('name', 'created_at', 'file')
    list_display_links = ('name', 'file',)
    readonly_fields = ('content',)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

admin.site.register(Report, ReportAdmin)
admin.site.register_view('report/export', view=AdminReportExport.as_view(),name=u'自定义导出表格')