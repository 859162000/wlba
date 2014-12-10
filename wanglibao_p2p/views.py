# encoding: utf8

import time
from copy import deepcopy
from operator import attrgetter
from decimal import Decimal
from hashlib import md5

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils import timezone, dateparse
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from rest_framework import status
from rest_framework import generics
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from marketing.models import SiteData
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_p2p.amortization_plan import get_amortization_plan
from wanglibao_p2p.forms import PurchaseForm
from wanglibao_p2p.keeper import ProductKeeper
from wanglibao_p2p.models import P2PProduct, P2PEquity, ProductAmortization, Warrant
from wanglibao_p2p.serializers import P2PProductSerializer
from wanglibao_p2p.trade import P2PTrader
from wanglibao_p2p.utility import validate_date, validate_status, handler_paginator, strip_tags
from wanglibao.const import ErrorNumber
from django.conf import settings
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_announcement.utility import AnnouncementP2P
from wanglibao_account.models import Binding
from django.contrib.auth.decorators import login_required
from wanglibao_account.utils import generate_contract_preview
from wanglibao_pay.util import get_a_uuid


REPAYMENTTYPEMAP = (
    (u'到期还本付息', 1),
    (u'等额本息', 2),
    (u'按月付息', 5),
    (u'按季度付息', 7)
)


class P2PDetailView(TemplateView):
    template_name = "p2p_detail.jade"

    def get_context_data(self, id, **kwargs):
        context = super(P2PDetailView, self).get_context_data(**kwargs)

        try:
            p2p = P2PProduct.objects.select_related('activity').get(pk=id, hide=False)
            form = PurchaseForm(initial={'product': p2p})

            if p2p.soldout_time:
                end_time = p2p.soldout_time
            else:
                end_time = p2p.end_time
        except P2PProduct.DoesNotExist:
            raise Http404(u'您查找的产品不存在')

        terms = get_amortization_plan(p2p.pay_method).generate(p2p.total_amount,
                                                               p2p.expected_earning_rate / 100,
                                                               p2p.amortization_count,
                                                               p2p.period)
        total_earning = terms.get("total") - p2p.total_amount

        total_fee_earning = 0

        if p2p.activity:
            total_fee_earning = Decimal(
                p2p.total_amount * p2p.activity.rule.rule_amount * (Decimal(p2p.period) / Decimal(12))).quantize(
                Decimal('0.01'))

        user = self.request.user
        current_equity = 0

        if user.is_authenticated():
            equity_record = p2p.equities.filter(user=user).first()
            if equity_record is not None:
                current_equity = equity_record.equity

            xunlei_vip = Binding.objects.filter(user=user).filter(btype='xunlei').first()
            context.update({
                'xunlei_vip': xunlei_vip
            })

        orderable_amount = min(p2p.limit_amount_per_user - current_equity, p2p.remain)

        site_data = SiteData.objects.all()[0]

        context.update({
            'p2p': p2p,
            'form': form,
            'end_time': end_time,
            'orderable_amount': orderable_amount,
            'total_earning': total_earning,
            'current_equity': current_equity,
            'site_data': site_data,
            'attachments': p2p.attachment_set.all(),
            'announcements': AnnouncementP2P,
            'total_fee_earning': total_fee_earning
        })

        return context


class PurchaseP2P(APIView):
    permission_classes = (IsAuthenticated,)

    @property
    def allowed_methods(self):
        return ['POST']

    def post(self, request):
        if not request.user.is_authenticated():
            return Response({
                                'message': u'请登录',
                                'error_number': ErrorNumber.unauthorized
                            }, status=status.HTTP_403_FORBIDDEN)
        if not request.user.wanglibaouserprofile.id_is_valid:
            return Response({
                                'message': u'请先进行实名认证',
                                'error_number': ErrorNumber.need_authentication
                            }, status=status.HTTP_400_BAD_REQUEST)
        form = PurchaseForm(request.DATA)

        if form.is_valid():
            p2p = form.cleaned_data['product']
            amount = form.cleaned_data['amount']

            try:
                trader = P2PTrader(product=p2p, user=request.user)
                product_info, margin_info, equity_info = trader.purchase(amount)
                return Response({
                    'data': product_info.amount
                })
            except Exception, e:
                return Response({
                                    'message': e.message,
                                    'error_number': ErrorNumber.unknown_error
                                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                                "message": form.errors,
                                'error_number': ErrorNumber.form_error
                            }, status=status.HTTP_400_BAD_REQUEST)


class PurchaseP2PMobile(APIView):
    permission_classes = (IsAuthenticated,)

    @property
    def allowed_methods(self):
        return ['POST']

    def post(self, request):

        if not request.user.is_authenticated():
            return Response({
                                'message': u'请登录',
                                'error_number': ErrorNumber.unauthorized
                            }, status=status.HTTP_200_OK)
        if not request.user.wanglibaouserprofile.id_is_valid:
            return Response({
                                'message': u'请先进行实名认证',
                                'error_number': ErrorNumber.need_authentication
                            }, status=status.HTTP_200_OK)
        form = PurchaseForm(request.DATA)
        phone = request.user.wanglibaouserprofile.phone
        if form.is_valid():
            p2p = form.cleaned_data['product']
            amount = form.cleaned_data['amount']

            try:
                trader = P2PTrader(product=p2p, user=request.user)
                product_info, margin_info, equity_info = trader.purchase(amount)
                return Response({
                    'data': product_info.amount
                })
            except Exception, e:
                return Response({
                                    'message': e.message,
                                    'error_number': ErrorNumber.unknown_error
                                }, status=status.HTTP_200_OK)
        else:
            return Response({
                                "message": form.errors,
                                'error_number': ErrorNumber.form_error
                            }, status=status.HTTP_200_OK)


class AuditProductView(TemplateView):
    template_name = 'audit_p2p.jade'

    def get_context_data(self, **kwargs):
        pk = kwargs['id']
        p2p = P2PProduct.objects.get(pk=pk)

        if p2p.status != u'满标待审核':
            return HttpResponse(u'产品状态不是满标待审核')

        return {
            "p2p": p2p
        }

    def post(self, request, **kwargs):
        pk = kwargs['id']
        p2p = P2PProduct.objects.select_related('activity__rule').get(pk=pk)
        ProductKeeper(p2p).audit(request.user)

        if p2p.activity:
            from celery.execute import send_task

            send_task("wanglibao_p2p.tasks.build_earning", kwargs={
                "product_id": pk
            })

        return HttpResponseRedirect('/' + settings.ADMIN_ADDRESS + '/wanglibao_p2p/p2pproduct/')


audit_product_view = staff_member_required(AuditProductView.as_view())


class CopyProductView(TemplateView):
    template_name = 'copy_p2p.jade'

    def get_context_data(self, **kwargs):
        pk = kwargs['id']
        p2p = P2PProduct.objects.get(pk=pk)


        return {
            "p2p": p2p
        }

    def post(self, request, **kwargs):
        pk = kwargs['id']
        p2p = P2PProduct.objects.get(pk=pk)
        # new_p2p = deepcopy(p2p)
        new_p2p = P2PProduct()
        new_p2p.id = None
        new_p2p.name = p2p.name + u"复制"+ get_a_uuid()
        new_p2p.short_name = p2p.short_name + u"复制"+ get_a_uuid()
        new_p2p.serial_number = p2p.serial_number + u"复制"+ get_a_uuid()
        new_p2p.contract_serial_number = p2p.contract_serial_number + u"复制"+ get_a_uuid()
        new_p2p.status = u"录标"
        new_p2p.period = p2p.period
        new_p2p.priority = 0
        new_p2p.expected_earning_rate = p2p.expected_earning_rate
        new_p2p.pay_method = p2p.pay_method
        new_p2p.repaying_source = p2p.repaying_source
        new_p2p.baoli_original_contract_number = p2p.baoli_original_contract_number
        new_p2p.baoli_original_contract_name = p2p.baoli_original_contract_name
        new_p2p.baoli_trade_relation = p2p.baoli_trade_relation
        new_p2p.borrower_name = p2p.borrower_name
        new_p2p.borrower_phone = p2p.borrower_phone
        new_p2p.borrower_address = p2p.borrower_address
        new_p2p.borrower_id_number = p2p.borrower_id_number
        new_p2p.borrower_bankcard = p2p.borrower_bankcard
        new_p2p.borrower_bankcard_type = p2p.borrower_bankcard_type
        new_p2p.borrower_bankcard_bank_name = p2p.borrower_bankcard_bank_name
        new_p2p.borrower_bankcard_bank_code = p2p.borrower_bankcard_bank_code
        new_p2p.borrower_bankcard_bank_province = p2p.borrower_bankcard_bank_province
        new_p2p.borrower_bankcard_bank_city = p2p.borrower_bankcard_bank_city
        new_p2p.borrower_bankcard_bank_branch = p2p.borrower_bankcard_bank_branch
        new_p2p.total_amount = p2p.total_amount
        new_p2p.extra_data = p2p.extra_data
        new_p2p.publish_time = timezone.now()
        new_p2p.end_time = timezone.now() + timezone.timedelta(days=7)
        new_p2p.limit_per_user = p2p.limit_per_user
        new_p2p.warrant_company = p2p.warrant_company
        new_p2p.usage = p2p.usage
        new_p2p.short_usage = p2p.short_usage
        new_p2p.contract_template = p2p.contract_template
        new_p2p.activity = p2p.activity
        # new_p2p.warrant_set = p2p.warrant_set
        new_p2p.save()
        warrants = Warrant.objects.filter(product=p2p)
        for warrant in warrants:
            new_warrant = Warrant()
            new_warrant.name = warrant.name
            new_warrant.product = new_p2p
            new_warrant.save()

        return HttpResponseRedirect('/' + settings.ADMIN_ADDRESS + '/wanglibao_p2p/p2pproduct/')


copy_product_view = staff_member_required(CopyProductView.as_view())


class P2PProductViewSet(PaginatedModelViewSet):
    model = P2PProduct
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = P2PProductSerializer
    paginate_by = 10

    def get_queryset(self):
        qs = super(P2PProductViewSet, self).get_queryset()

        maxid = self.request.QUERY_PARAMS.get('maxid', '')
        minid = self.request.QUERY_PARAMS.get('minid', '')

        pager = None
        if maxid and not minid:
            pager = Q(id__gt=maxid)
        if minid and not maxid:
            pager = Q(id__lt=minid)

        if pager:
            return qs.filter(hide=False).filter(status__in=[
                u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标'
            ]).filter(pager).order_by('-priority')
        else:
            return qs.filter(hide=False).filter(status__in=[
                u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标'
            ]).order_by('-priority')


P2PEYE_PAY_WAY = {
    u'等额本息': 1,
    u'按月付息': 2,
    u'到期还本付息': 4,
    u'按季度付息': 5,
}


class P2PEyeListAPIView(APIView):
    """ 网贷天眼 API
    """
    permission_classes = (IsAdminUserOrReadOnly, )

    def get(self, request):

        result = {
            "result_code": -1,
            "result_msg": u"未授权的访问!",
            "page_count": "null",
            "page_index": "null",
            "loans": "null"
        }

        # 验证状态
        status_query, status, result = validate_status(request, result, 'status')
        if not status_query:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        # 验证日期
        time_from, result = validate_date(request, result, 'time_from')
        if not time_from:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        time_to, result = validate_date(request, result, 'time_to')
        if not time_to:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))
        # 构造日期查询语句
        publish_query = Q(publish_time__range=(time_from, time_to))

        p2pproducts = P2PProduct.objects.select_related('activity').filter(hide=False).filter(status_query).filter(
            publish_query)

        # 分页处理
        p2pproducts, paginator = handler_paginator(request, p2pproducts)
        if not p2pproducts:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        if p2pproducts:
            loans = []
            for p2pproduct in p2pproducts:
                # 进度
                amount = Decimal.from_float(p2pproduct.total_amount).quantize(Decimal('0.00'))
                percent = p2pproduct.ordered_amount / amount
                # process = percent.quantize(Decimal('0.0'), 'ROUND_DOWN')

                reward = 0
                if p2pproduct.activity:
                    reward = p2pproduct.activity.rule.rule_amount
                rate = p2pproduct.expected_earning_rate + float(reward * 100)
                rate = rate / 100

                obj = {
                    "id": str(p2pproduct.id),
                    "platform_name": u"网利宝",
                    "url": "https://www.wanglibao.com/p2p/detail/%s" % p2pproduct.id,
                    "title": p2pproduct.name,
                    "username": md5(p2pproduct.borrower_name.encode('utf-8')).hexdigest(),
                    "status": status,
                    "userid": md5(p2pproduct.borrower_name.encode('utf-8')).hexdigest(),
                    "c_type": u"抵押标" if p2pproduct.category == u'证大速贷' else u"信用标",
                    "amount": str(p2pproduct.total_amount),
                    "rate": str(rate),
                    "period": u'{}个月'.format(p2pproduct.period),
                    "pay_way": str(P2PEYE_PAY_WAY.get(p2pproduct.pay_method, 0)),
                    "process": percent,
                    "reward": str(reward),
                    "guarantee": "null",
                    "start_time": time_from.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": timezone.localtime(p2pproduct.end_time).strftime("%Y-%m-%d %H:%M:%S"),
                    "invest_num": str(p2pproduct.equities.count()),
                    "c_reward": "0"
                }
                loans.append(obj)
            result.update(loans=loans, page_count=paginator.num_pages, page_index=p2pproducts.number, result_code="1",
                          result_msg=u'获取数据成功!')
        else:
            result.update(result_code='-1', result_msg=u'未授权的访问!')
        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))


class P2PEyeEquityAPIView(APIView):
    permission_classes = (IsAdminUserOrReadOnly, )

    def get(self, request):
        result = {
            "result_code": "-1",
            "result_msg": u"未授权的访问!",
            "page_count": "null",
            "page_index": "null",
            "data": "null"
        }
        try:
            id = int(request.GET.get('id'))
            id_query = Q(id=id)
        except:
            result.update(result_code=-2, result_msg=u'id参数不存在或者格式错误')
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        # 验证日期
        time_from, result = validate_date(request, result, 'time_from')
        if not time_from:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        time_to, result = validate_date(request, result, 'time_to')
        if not time_to:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))
        # 构造日期查询语句
        publish_query = Q(publish_time__range=(time_from, time_to))

        try:
            p2pproduct = P2PProduct.objects.filter(hide=False).filter(status__in=[
                u'正在招标', u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中'
            ]).filter(publish_query).get(id_query)
        except:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        p2pequities = p2pproduct.equities.all()

        if not p2pequities:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        # 分页处理
        equities, paginator = handler_paginator(request, p2pequities)
        if not equities:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))

        data = []
        for eq in equities:
            obj = {
                "id": str(p2pproduct.id),
                "link": "https://www.wanglibao.com/p2p/detail/%s" % p2pproduct.id,
                "useraddress": "null",
                "username": eq.user.username,
                "userid": str(eq.user.id),
                "type": u"手动",
                "money": str(eq.equity),
                "account": str(eq.equity),
                "status": u"成功",
                "add_time": timezone.localtime(eq.created_at).strftime("%Y-%m-%d %H:%M:%S"),
            }
            data.append(obj)
        result.update(data=data, page_count=str(paginator.num_pages), page_index=str(equities.number), result_code="1",
                      result_msg=u'获取数据成功!')
        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))


class XunleiP2PListAPIView(APIView):
    permission_classes = ()

    def get(self, request):
        now = time.mktime(timezone.now().timetuple())
        uid = request.GET.get('xluid')
        project_list = []

        result = {
            'timestamp': str(now),
            'project_list': project_list
        }
        p2pproducts = P2PProduct.objects.filter(hide=False).filter(status=u'正在招标')[0:5]

        for p2pproduct in p2pproducts:
            income = Decimal('0')
            amorts = p2pproduct.amortizations.all()
            for amort in amorts:
                income += amort.interest
            income = income / 10000
            income = income.quantize(Decimal('0.00'))

            # 进度
            amount = Decimal.from_float(p2pproduct.total_amount).quantize(Decimal('0.00'))
            percent = (p2pproduct.ordered_amount / amount) * 100
            percent = percent.quantize(Decimal('0.00'))

            obj = {
                'id': str(p2pproduct.id),
                'title': p2pproduct.name,
                'title_url': 'https://www.wanglibao.com/p2p/detail/%s?xluid=%s' % (p2pproduct.id, uid),
                'rate_year': str(p2pproduct.expected_earning_rate),
                'rate_vip': str(1),
                'income': str(income),
                'finance': str(p2pproduct.total_amount),
                'min_invest': str(p2pproduct.limit_amount_per_user),
                'guarantor': str(p2pproduct.warrant_company.name),
                'finance_progress': str(percent),
                'finance_left': str(p2pproduct.remain),
                'repayment_period': str(p2pproduct.period * 30),
                'repayment_type': str(P2PEYE_PAY_WAY.get(p2pproduct.pay_method, 0)),
                'buy_url': 'https://www.wanglibao.com/p2p/detail/%s?xluid=%s' % (p2pproduct.id, uid),
                'finance_start_time': str(time.mktime(timezone.localtime(p2pproduct.publish_time).timetuple())),
                'finance_end_time': str(time.mktime(timezone.localtime(p2pproduct.end_time).timetuple())),
                # 'repayment_time': time.mktime(timezone.localtime(amorts.first().term_date).timetuple()),
                'status': p2pproduct.status
            }
            project_list.append(obj)
        result.update(project_list=project_list)
        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))


class XunleiP2PbyUser(APIView):
    permission_classes = ()

    def get(self, reqeust):
        uid = reqeust.GET.get('xluid')
        if not uid:
            return HttpResponse(
                renderers.JSONRenderer().render({'code': -1, 'message': u'xluid错误'}, 'application/json'))
        my_project = []

        p2p_equities = P2PEquity.objects.filter(user__id=uid).filter(product__status__in=[
            u'已完成', u'满标待打款',u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标',
        ]).select_related('product')

        income_all = 0
        for equity in p2p_equities:
            if equity.confirm:
                income_all += equity.total_interest

        result = {
            'income_all': income_all,
            'my_project': my_project
        }

        p2pequities = p2p_equities.filter(product__status=u'正在招标')

        for p2pequity in p2pequities:
            p2pproduct = p2pequity.product

            # 进度
            amount = Decimal.from_float(p2pproduct.total_amount).quantize(Decimal('0.00'))
            percent = (p2pproduct.ordered_amount / amount) * 100
            percent = percent.quantize(Decimal('0.00'))

            obj = {
                'id': str(p2pproduct.id),
                'title': p2pproduct.name,
                'title_url': 'https://www.wanglibao.com/p2p/detail/%s?xluid=%s' % (p2pproduct.id, uid),
                'finance_start_time': str(time.mktime(timezone.localtime(p2pproduct.publish_time).timetuple())),
                'finance_end_time': str(time.mktime(timezone.localtime(p2pproduct.end_time).timetuple())),
                'cur_income': '0',
                'investment': str(p2pequity.equity),
                'repayment_progress': percent,
            }
            my_project.append(obj)
        result.update(my_project=my_project)
        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))


class P2PProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    model = P2PProduct
    permission_classes = IsAdminUserOrReadOnly,
    serializer_class = P2PProductSerializer
    queryset = P2PProduct.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class GetNoWProjectsAPI(APIView):
    """
    网贷之家数据接口， 获取正在招标的数据
    """
    # todo 合并代码
    permission_classes = (IsAdminUserOrReadOnly,)

    def get(self, request):

        p2pproducts = P2PProduct.objects.filter(hide=False).filter(status=u'正在招标')

        p2p_list = []
        for p2p in p2pproducts:

            amount = Decimal.from_float(p2p.total_amount).quantize(Decimal('0.00'))
            percent = p2p.ordered_amount / amount * 100
            # percent = 1499900 / Decimal.from_float(1500000) * 100
            schedule = '{}%'.format(percent.quantize(Decimal('0.0'), 'ROUND_DOWN'))

            if p2p.category == u'证大速贷':
                type = u"信用标"
            type = u"抵押标"

            for pay_method, value in REPAYMENTTYPEMAP:
                if pay_method == p2p.pay_method:
                    repaymentType = value
                    break

            p2pequities = p2p.equities.all()
            subscribes = []
            for eq in p2pequities:
                temp_eq = {
                    "subscribeUserName": eq.user.username,
                    "amount": Decimal.from_float(eq.equity).quantize(Decimal('0.00')),
                    "validAmount": Decimal.from_float(eq.equity).quantize(Decimal('0.00')),
                    "addDate": timezone.localtime(eq.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "1",
                    "type": "0"
                }
                subscribes.append(temp_eq)

            temp_p2p = {
                "projectId": str(p2p.pk),
                "title": p2p.name,
                "amount": amount,
                "schedule": schedule,
                "interestRate": '{}%'.format(p2p.expected_earning_rate - p2p.excess_earning_rate),
                "deadline": str(p2p.period),
                "deadlineUnit": u"月",
                "reward": '{}%'.format(p2p.excess_earning_rate),
                "type": type,
                "repaymentType": str(repaymentType),
                "subscribes": subscribes,
                "userName": md5(p2p.borrower_bankcard_bank_name.encode('utf-8')).hexdigest(),
                "amountUsedDesc": strip_tags(p2p.short_usage),
                "loanUrl": "https://www.wanglibao.com/p2p/detail/%s" % p2p.id,
                # "successTime": p2p.soldout_time,
                "publishTime": timezone.localtime(p2p.publish_time).strftime("%Y-%m-%d %H:%M:%S")
            }
            p2p_list.append(temp_p2p)

        return HttpResponse(renderers.JSONRenderer().render(p2p_list, 'application/json'))


class GetProjectsByDateAPI(APIView):
    """
    网贷之家数据接口， 获取已经完成的数据
    """

    permission_classes = (IsAdminUserOrReadOnly,)

    def get(self, request):

        date = request.GET.get('date', '')
        if not date:
            return HttpResponse(renderers.JSONRenderer().render({'message': u'错误的date'}, 'application/json'))

        date = [int(i) for i in date.split('-')]
        start_time = timezone.datetime(*date)
        end_time = start_time + timezone.timedelta(days=1)

        p2pproducts = P2PProduct.objects.filter(hide=False).filter(status__in=[
            u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'已完成'
        ]).filter(soldout_time__range=(start_time, end_time))

        p2p_list = []
        for p2p in p2pproducts:

            amount = Decimal.from_float(p2p.total_amount).quantize(Decimal('0.00'))
            percent = p2p.ordered_amount / amount * 100
            schedule = '{}%'.format(percent.quantize(Decimal('0.0'), 'ROUND_DOWN'))

            if p2p.category == u'证大速贷':
                type = u"信用标"
            type = u"抵押标"

            for pay_method, value in REPAYMENTTYPEMAP:
                if pay_method == p2p.pay_method:
                    repaymentType = value
                    break

            p2pequities = p2p.equities.all()
            subscribes = []
            for eq in p2pequities:
                temp_eq = {
                    "subscribeUserName": eq.user.username,
                    "amount": Decimal.from_float(eq.equity).quantize(Decimal('0.00')),
                    "validAmount": Decimal.from_float(eq.equity).quantize(Decimal('0.00')),
                    "addDate": timezone.localtime(eq.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "1",
                    "type": "0"
                }
                subscribes.append(temp_eq)

            temp_p2p = {
                "projectId": str(p2p.pk),
                "title": p2p.name,
                "amount": amount,
                "schedule": schedule,
                "interestRate": '{}%'.format(p2p.expected_earning_rate - p2p.excess_earning_rate),
                "deadline": str(p2p.period),
                "deadlineUnit": u"月",
                "reward": '{}%'.format(p2p.excess_earning_rate),
                "type": type,
                "repaymentType": str(repaymentType),
                "subscribes": subscribes,
                "userName": md5(p2p.borrower_bankcard_bank_name.encode('utf-8')).hexdigest(),
                "amountUsedDesc": strip_tags(p2p.short_usage),
                "loanUrl": "https://www.wanglibao.com/p2p/detail/%s" % p2p.id,
                "successTime": timezone.localtime(p2p.soldout_time).strftime("%Y-%m-%d %H:%M:%S"),
                "publishTime": timezone.localtime(p2p.publish_time).strftime("%Y-%m-%d %H:%M:%S")
            }
            p2p_list.append(temp_p2p)

        return HttpResponse(renderers.JSONRenderer().render(p2p_list, 'application/json'))


class P2PListAPI(APIView):
    """ 和讯网 API
    """
    permission_classes = (IsAdminUserOrReadOnly, )

    def get(self, request):

        date_args = request.GET.get('date', '')
        if not date_args:
            return HttpResponse(
                renderers.JSONRenderer().render({'message': u'date必传', 'code': -2}, 'application/json'))
        try:
            start_time = dateparse.parse_date(date_args)

            if not start_time:
                return HttpResponse(
                    renderers.JSONRenderer().render({'message': u'错误的date', 'code': -1}, 'application/json'))
        except:
            return HttpResponse(
                renderers.JSONRenderer().render({'message': u'错误的date', 'code': -1}, 'application/json'))

        p2pproducts = P2PProduct.objects.filter(hide=False) \
            .filter(status=u'正在招标').filter(publish_time__gte=start_time)

        p2p_list = []
        for p2p in p2pproducts:
            amount = Decimal.from_float(p2p.total_amount).quantize(Decimal('0.00'))
            percent = p2p.ordered_amount / amount * 100
            fld_lend_progress = percent.quantize(Decimal('0.0'), 'ROUND_DOWN')

            p2pequity_count = p2p.equities.all().count()

            temp_p2p = {
                "fld_proname": p2p.name,
                "fld_name": u'网利宝',
                "fld_finstarttime": timezone.localtime(p2p.publish_time).strftime("%Y-%m-%d %H:%M:%S"),
                "fld_finendtime": timezone.localtime(p2p.end_time).strftime("%Y-%m-%d %H:%M:%S"),
                "fld_total_finance": p2p.total_amount,
                "fld_lend_period": p2p.period * 30,
                "fld_interest_year": p2p.expected_earning_rate,
                "fld_guarantee_org": p2p.warrant_company.name,
                "fld_mininvest": 100.0,
                "fld_awards": 1 if p2p.activity else 0,
                "fld_lend_progress": fld_lend_progress,
                "fld_invest_number": p2pequity_count,
                "fld_finance_left": p2p.total_amount - p2p.ordered_amount
            }
            p2p_list.append(temp_p2p)

        return HttpResponse(renderers.JSONRenderer().render(p2p_list, 'application/json'))


class RecordView(APIView):
    permission_classes = ()

    def get(self, request, product_id):
        try:
            product = P2PProduct.objects.get(pk=product_id)
        except P2PProduct.DoesNotExist:
            return Response(
                status=404
            )

        equities = product.p2precord_set.filter(catalog=u'申购').prefetch_related('user').prefetch_related(
            'user__wanglibaouserprofile')

        record = [{
                      "amount": float(eq.amount),
                      "user": eq.user.wanglibaouserprofile.phone,
                      "create_time": timezone.localtime(eq.create_time).strftime("%Y-%m-%d %H:%M:%S")
                  } for eq in equities]

        return Response(record)


class P2PListView(TemplateView):
    template_name = 'p2p_list.jade'

    def get_context_data(self, **kwargs):

        p2p_done = P2PProduct.objects.select_related('warrant_company', 'activity').filter(hide=False).filter(
            Q(publish_time__lte=timezone.now())) \
            .filter(status=u'正在招标').order_by('-publish_time')

        p2p_others = P2PProduct.objects.select_related('warrant_company', 'activity').filter(hide=False).filter(
            Q(publish_time__lte=timezone.now())).filter(
            status__in=[
                u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中'
            ]).order_by('-soldout_time')

        show_slider = False
        if p2p_done:
            show_slider = True
            p2p_earning = sorted(p2p_done, key=lambda x: (-x.expected_earning_rate, x.available_amout))
            p2p_period = sorted(p2p_done, key=lambda x: (x.period, x.available_amout))
            p2p_amount = sorted(p2p_done, key=attrgetter('available_amout'))
        else:
            p2p_earning = p2p_period = p2p_amount = []

        p2p_products = []
        p2p_products.extend(p2p_done)
        p2p_products.extend(p2p_others)

        limit = 10
        paginator = Paginator(p2p_products, limit)
        page = self.request.GET.get('page')

        try:
            p2p_products = paginator.page(page)
        except PageNotAnInteger:
            p2p_products = paginator.page(1)
        except Exception:
            p2p_products = paginator.page(paginator.num_pages)

        return {
            'p2p_products': p2p_products,
            'p2p_earning': p2p_earning[:5],
            'p2p_period': p2p_period[:5],
            'p2p_amount': p2p_amount[:5],
            'show_slider': show_slider,
            'announcements': AnnouncementP2P
        }


class GenP2PUserProfileReport(TemplateView):
    template_name = 'gen_p2p_user_profile_report.jade'


class AdminP2PUserRecord(TemplateView):
    template_name = 'p2p_user_record.jade'

    def get_context_data(self, **kwargs):
        p2p_id = self.request.GET['p2p_id']
        p2pequity = P2PEquity.objects.filter(product__id=p2p_id)

        return {
            'p2pequity': p2pequity
        }


@login_required
def preview_contract(request, id):
    product = P2PProduct.objects.filter(id=id).first()
    if not product:
        # if product.status == u'录标' or product.status == u'录标完成':
        # return HttpResponse(u'<h3 style="color:red;">【录标完成】之后才能进行合同预览！</h3>')
        # else:
        return HttpResponse(u'<h3 style="color:red;">没有该产品或产品信息错误！</h3>')

    equity = ProductAmortization.objects.filter(product_id=id).prefetch_related('product')
    return HttpResponse(generate_contract_preview(equity, product))