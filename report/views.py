# -*- coding: utf-8 -*-
import time
import datetime
from django.utils import timezone
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.db.models import Sum
from report.reports import DepositReportGenerator, WithDrawReportGenerator, ProductionRecordReportGenerator, \
    PaybackReportGenerator, ProductionAmortizationsReportGenerator, P2PAuditReportGenerator, \
    EearningReportGenerator, WithDrawDetailReportGenerator, P2PstatusReportGenerator, ClientInfoGenerator, \
    RedpackReportGenerator, ProductionAmortizationsReportAllGenerator
from wanglibao_margin.models import Margin

type = (
    (u'充值', 0),
    (u'提现', 1),
    (u'产品流水', 2),
    (u'产品还款', 3),
    (u'用户还款', 4),
    (u'满标复审', 5),
    (u'赠送记录', 6),
    (u'提现详细记录', 7),
    (u'满标状态变化', 8),
    (u'客户端信息', 9),
    (u'红包流水', 10),
    (u'产品还款计划all', 11)
)


class AdminReportExport(TemplateView):
    template_name = 'report_export.jade'

    def get_context_data(self, **kwargs):
        today = timezone.datetime.today()
        yestoday = timezone.datetime.today() - timezone.timedelta(days=2)

        margin = Margin.objects.all().aggregate(Sum('margin'))['margin__sum']
        freeze = Margin.objects.all().aggregate(Sum('freeze'))['freeze__sum']
        withdrawing = Margin.objects.all().aggregate(Sum('withdrawing'))['withdrawing__sum']

        return {
            'yestoday': yestoday.strftime("%Y-%m-%d %H:%M:%S"),
            'today': today.strftime("%Y-%m-%d %H:%M:%S"),
            'type': type,
            'margin': margin,
            'freeze': freeze,
            'withdrawing': withdrawing
        }

    def post(self, request, **kwargs):
        start_time = self._timeformat(request.POST.get('start_time'))
        end_time = self._timeformat(request.POST.get('end_time'))
        type = request.POST.get('type')

        if type == '0':
            self._generate_desposite(request, start_time, end_time)
        if type == '1':
            self._generate_withdraw(request, start_time, end_time)
        if type == '2':
            self._generate_production_record(request, start_time, end_time)
        if type == '3':
            self._generate_production_amortizations(request, start_time, end_time)
        if type == '4':
            self._generate_user_amortizations(request, start_time, end_time)
        if type == '5':
            self._generate_p2paudit(request, start_time, end_time)
        if type == '6':
            self._generate_earning(request, start_time, end_time, request.POST.get('earning_type'))
        if type == '7':
            self._generate_withdrawdetail(request, start_time, end_time)
        if type == '8':
            self._generate_p2pstatus(request, start_time, end_time)
        if type == '9':
            self._generate_clientinfo(request, start_time, end_time)
        if type == '10':
            self._generate_redpackdrecord(request, start_time, end_time)
        if type == '11':
            self._generate_production_amortizations_all(request, start_time, end_time)

        return HttpResponseRedirect('export')

    def _generate_desposite(self, request, start_time, end_time):
        self._apply_generate(request, start_time, end_time, DepositReportGenerator, u'充值表格')

    def _generate_withdraw(self, request, start_time, end_time):
        self._apply_generate(request, start_time, end_time, WithDrawReportGenerator, u'提现表格')

    def _generate_production_record(self, request, start_time, end_time):
        self._apply_generate(request, start_time, end_time, ProductionRecordReportGenerator, u'产品流水')

    def _generate_production_amortizations(self, request, start_time, end_time):
        self._apply_generate(request, start_time, end_time, ProductionAmortizationsReportGenerator, u'产品还款')

    def _generate_user_amortizations(self, request, start_time, end_time):
        self._apply_generate(request, start_time, end_time, PaybackReportGenerator, u'用户还款')

    def _generate_p2paudit(self, request, start_time, end_time):
        self._apply_generate(request, start_time, end_time, P2PAuditReportGenerator, u'满标复审')

    def _generate_earning(self, request, start_time, end_time, type):
        print type, 'type........'
        self._apply_generate(request, start_time, end_time, EearningReportGenerator, u'赠送记录', type=type)

    def _generate_withdrawdetail(self, request, start_time, end_time):
        self._apply_generate(request, start_time, end_time, WithDrawDetailReportGenerator, u'提现详细记录')

    def _generate_p2pstatus(self, request, start_time, end_time):
        self._apply_generate(request, start_time, end_time, P2PstatusReportGenerator, u'满标状态变化')

    def _generate_clientinfo(self, request, start_time, end_time):
        self._apply_generate(request, start_time, end_time, ClientInfoGenerator, u'客户端信息')

    def _generate_redpackdrecord(self, request, start_time, end_time):
        self._apply_generate(request, start_time, end_time, RedpackReportGenerator, u'红包流水')

    def _generate_production_amortizations_all(self, request, start_time, end_time):
        self._apply_generate(request, start_time, end_time, ProductionAmortizationsReportAllGenerator, u'产品还款计划all')

    def _apply_generate(self, request, start_time, end_time, cls, message='', type=None):
        print type, 'type........'
        try:
            if type:
                cls.generate_report(start_time, end_time, type=type)
            else:
                cls.generate_report(start_time, end_time)
            messages.info(
                request, u'生成{}成功，请到'
                         u'<a href="/AK7WtEQ4Q9KPs8Io_zOncw/report/report" />导出表格处 </a> 查看'.format(message))
        except Exception, e:
            messages.info(request, u'导出失败，请重新生成.错误信息{}'.format(e))

    def _timeformat(self, str_time):
        return datetime.datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S")
