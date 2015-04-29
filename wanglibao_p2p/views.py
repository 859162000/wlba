# encoding: utf8

from operator import attrgetter
from decimal import Decimal
import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from rest_framework import status
from rest_framework import generics, renderers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from marketing.models import SiteData
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_p2p.amortization_plan import get_amortization_plan
from wanglibao_p2p.prepayment import PrepaymentHistory
from wanglibao_p2p.forms import PurchaseForm, BillForm
from wanglibao_p2p.keeper import ProductKeeper, EquityKeeperDecorator
from wanglibao_p2p.models import P2PProduct, P2PEquity, ProductAmortization, Warrant, UserAmortization, \
    P2PProductContract, InterestPrecisionBalance
from wanglibao_p2p.serializers import P2PProductSerializer
from wanglibao_p2p.trade import P2PTrader
from wanglibao_p2p.utility import validate_date, validate_status, handler_paginator, strip_tags, AmortizationCalculator
from wanglibao.const import ErrorNumber
from django.conf import settings
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_announcement.utility import AnnouncementP2P
from wanglibao_account.models import Binding
from django.contrib.auth.decorators import login_required
from wanglibao_account.utils import generate_contract_preview
from wanglibao_pay.util import get_a_uuid
from django.contrib import messages
from django.shortcuts import redirect, render_to_response
from marketing.utils import save_client
from marketing.tops import Top
from order.utils import OrderHelper
from wanglibao_redpack import backends
from wanglibao_rest import utils
from exceptions import PrepaymentException

class P2PDetailView(TemplateView):
    template_name = "p2p_detail.jade"

    def get_context_data(self, id, **kwargs):
        context = super(P2PDetailView, self).get_context_data(**kwargs)

        try:
            #p2p = P2PProduct.objects.select_related('activity').get(pk=id, hide=False).exclude(status=u'流标')
            p2p = P2PProduct.objects.select_related('activity').exclude(status=u'流标').exclude(status=u'录标').get(pk=id, hide=False)
            form = PurchaseForm(initial={'product': p2p})

            if p2p.soldout_time:
                end_time = p2p.soldout_time
            else:
                end_time = p2p.end_time
        except P2PProduct.DoesNotExist:
            raise Http404(u'您查找的产品不存在')

        terms = get_amortization_plan(p2p.pay_method).generate(p2p.total_amount,
                                                               p2p.expected_earning_rate / 100,
                                                               datetime.datetime.now(),
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
                'xunlei_vip': xunlei_vip,
                'is_invested': user.wanglibaouserprofile.is_invested
            })

        orderable_amount = min(p2p.limit_amount_per_user - current_equity, p2p.remain)

        site_data = SiteData.objects.all()[0]
        #排行榜

        top = Top()
        day_tops = top.day_tops(datetime.datetime.now())
        week_tops = Top().week_tops(datetime.datetime.now())
        all_tops = Top().all_tops()

        device = utils.split_ua(self.request)
        red_packets = backends.list_redpack(user, 'available', device['device_type'])

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
            'total_fee_earning': total_fee_earning,
            'day_tops': day_tops,
            'week_tops': week_tops,
            'all_tops': all_tops,
            'is_valid': top.is_valid(),
            'red_packets': len(red_packets['packages']['available'])
        })

        return context


class PurchaseP2P(APIView):
    permission_classes = (IsAuthenticated,)

    @property
    def allowed_methods(self):
        return ['POST']

    def p2p_form(self, request):
        p2p_id = request.DATA.get("product", "").strip()
        category = P2PProduct.objects.filter(pk=p2p_id)[0].category
        if category and category == '票据':
            form = BillForm(request.DATA)
        else:
            form = PurchaseForm(request.DATA)

        return form

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

        # p2p_id = request.DATA.get("product", "").strip()
        # category = P2PProduct.objects.filter(pk=p2p_id)[0].category
        # if category and category == '票据':
        #     form = BillForm(request.DATA)
        # else:
        #     form = PurchaseForm(request.DATA)

        form = self.p2p_form(request)

        if form.is_valid():
            p2p = form.cleaned_data['product']
            amount = form.cleaned_data['amount']

            redpack = request.DATA.get("redpack", "")
            if redpack and not redpack.isdigit():
                return Response({
                                    'message': u'请输入有效红包',
                                    'error_number': ErrorNumber.unknown_error
                                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                trader = P2PTrader(product=p2p, user=request.user, request=request)
                product_info, margin_info, equity_info = trader.purchase(amount, redpack)

                return Response({
                    'data': product_info.amount,
                    'category': equity_info.product.category
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
            redpack = request.DATA.get("redpack", "")
            if redpack and not redpack.isdigit():
                return Response({
                                    'message': u'请输入有效红包',
                                    'error_number': ErrorNumber.need_authentication
                                }, status=status.HTTP_200_OK)

            try:
                trader = P2PTrader(product=p2p, user=request.user, request=request)
                product_info, margin_info, equity_info = trader.purchase(amount, redpack)

                # save client info
                save_client(request, phone=phone, action=1)

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

        equities = p2p.equities.all()[:20]
        amortizations_plan = p2p.amortizations.all()

        if p2p.status != u'满标待审核':
            return HttpResponse(u'产品状态不是满标待审核')

        return {
            "p2p": p2p,
            "equities": equities,
            "product_amortizations": amortizations_plan,
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


class AuditAmortizationView(TemplateView):
    template_name = 'audit_amortization.jade'

    def get_context_data(self, **kwargs):
        pk = kwargs['id']
        #page = kwargs.get('page', 1)
        page = self.request.GET.get('page', 1)

        p2p_amortization = ProductAmortization.objects.filter(pk=pk).first()
        user_amortizations = p2p_amortization.subs.all().select_related('user__wanglibaouserprofile')

        limit = 30
        paginator = Paginator(user_amortizations, limit)

        try:
            user_amortizations = paginator.page(page)
        except PageNotAnInteger:
            user_amortizations = paginator.page(1)
        except Exception:
            user_amortizations = paginator.page(paginator.num_pages)

        return {
            "p2p_amortization": p2p_amortization,
            "user_amortizations": user_amortizations
            }


class AuditEquityView(TemplateView):
    template_name = 'audit_equity.jade'

    def get_context_data(self, **kwargs):
        pk = kwargs['id']
        #page = kwargs.get('page', 1)
        page = self.request.GET.get('page', 1)

        p2p = P2PProduct.objects.filter(pk=pk).first()

        equities = p2p.equities.all()

        limit = 30
        paginator = Paginator(equities, limit)

        try:
            equities = paginator.page(page)
        except PageNotAnInteger:
            equities = paginator.page(1)
        except Exception:
            equities = paginator.page(paginator.num_pages)

        if p2p.status != u'满标待审核':
            return HttpResponse(u'产品状态不是满标待审核')

        return {
            "equities": equities,
            "p2p": p2p
            }


audit_product_view = staff_member_required(AuditProductView.as_view())
audit_equity_view = staff_member_required(AuditEquityView.as_view())
audit_amortization_view = staff_member_required(AuditAmortizationView.as_view())


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
        new_p2p.name = p2p.name + u"复制" + get_a_uuid()
        new_p2p.short_name = p2p.short_name + u"复制" + get_a_uuid()
        new_p2p.serial_number = p2p.serial_number + u"复制" + get_a_uuid()
        new_p2p.contract_serial_number = p2p.contract_serial_number + u"复制" + get_a_uuid()
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
            ]).filter(~Q(category=u'票据')).filter(pager).order_by('-priority', '-publish_time')
        else:
            return qs.filter(hide=False).filter(status__in=[
                u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标'
            ]).filter(~Q(category=u'票据')).order_by('-priority', '-publish_time')


class P2PProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    model = P2PProduct
    permission_classes = IsAdminUserOrReadOnly,
    serializer_class = P2PProductSerializer
    queryset = P2PProduct.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


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


class AdminAmortization(TemplateView):
    template_name = 'admin_amortization.jade'

    def post(self, request, **kwargs):
        try:
            paymethod = request.POST.get('paymethod')
            amount = request.POST.get('amount')
            year_rate = float(request.POST.get('year_rate')) / 100
            period = int(request.POST.get('period'))
        except:
            messages.warning(request, u'输入错误, 请重新检测')
            return redirect('./amortization')

        if amount and year_rate and period:
            ac = AmortizationCalculator(paymethod, amount, year_rate, period)
            acs = ac.generate()
            total = acs['total']
            terms = acs['terms']
            key = ('term_amount', 'principal', 'interest', 'principal_left')
            newterms = [dict(zip(key, term)) for term in terms]
            return render_to_response('admin_amortization.jade', {'total': total, 'newterms': newterms})
        else:
            messages.warning(request, u'查询错误')
            return redirect('./amortization')


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
    equity_all = P2PEquity.objects.select_related('user__wanglibaouserprofile', 'product__contract_template') \
        .select_related('product').filter(product=product).all()
    productAmortizations = ProductAmortization.objects.filter(product_id=id).select_related('product').all()
    contract_info = P2PProductContract.objects.filter(product=product).first()
    product.contract_info = contract_info
    product.equity_all = equity_all
    product.total_interest_actual = InterestPrecisionBalance.objects.filter(equity__product=product) \
        .aggregate(actual_sum=Sum('interest_actual'))

    return HttpResponse(generate_contract_preview(productAmortizations, product))


def AuditEquityCreateContract(request, equity_id):
    equity = P2PEquity.objects.filter(id=equity_id).select_related('product').first()
    product = equity.product
    order = OrderHelper.place_order(order_type=u'生成合同文件', status=u'开始', equity_id=equity_id, product_id=product.id)

    if not equity.latest_contract:
        #create contract file
        EquityKeeperDecorator(product, order.id).generate_contract_one(equity_id=equity_id, savepoint=False)

    equity_new = P2PEquity.objects.filter(id=equity_id).first()
    try:
        f = equity_new.latest_contract
        lines = f.readlines()
        f.close()
        return HttpResponse("\n".join(lines))
    except ValueError, e:
        raise Http404


class AdminP2PList(TemplateView):
    template_name = 'admin_p2plist.jade'

    def get_context_data(self, **kwargs):
        name = self.request.GET.get('p2p_name', False)
        if name:
            p2p_list = P2PProduct.objects.filter(status=u'还款中', name=name) \
                    .select_related('amortizations') \
                    .order_by('-id')
        else:
            p2p_list = P2PProduct.objects.filter(status=u'还款中') \
                    .select_related('amortizations') \
                    .order_by('-id')

        return {
            'p2p_list': p2p_list
            }

class AdminPrepayment(TemplateView):
    template_name = 'admin_prepayment.jade'

    def get_context_data(self, **kwargs):
        id = kwargs['id']
        if id:
            p2p = P2PProduct.objects.filter(pk=id).select_related('amortizations')
        if p2p[0].status != u'还款中':
            return {
                    'p2p': None,
                    'amortizations': []
                    }
        
        return {
            'p2p': p2p[0],
            'amortizations': p2p[0].amortizations.all(),
            'default_date': datetime.datetime.now().strftime('%Y-%m-%d')
            }



class RepaymentAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        repayment_date = request.DATA.get('repayment_date', "")
        repayment_type = request.DATA.get('repayment_type', "")
        repayment_now = request.DATA.get('now', "0")
        penal_interest = request.DATA.get('penal_interest', 0)
        if penal_interest == '':
            penal_interest = Decimal(0)
        else:
            penal_interest = Decimal(penal_interest)

        id = request.POST.get('id')

        p2p = P2PProduct.objects.filter(pk=id)
        p2p = p2p[0]

        from dateutil import parser
        flag_date = parser.parse(repayment_date)

        try:
            payment = PrepaymentHistory(p2p, flag_date)
            if repayment_now == '1':
                record = payment.prepayment(penal_interest, repayment_type, flag_date)
            else:
                record = payment.get_product_repayment(Decimal(0), repayment_type, flag_date)

            result = {
                    'errno': 0,
                    'principal': record.principal,
                    'interest': record.interest,
                    'penal_interest': record.penal_interest,
                    'date': repayment_date
                    }
        except PrepaymentException:
            result = {
                    'errno': 1,
                    'errmessage': u'你的还款计划有问题'
                    }

        return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))
