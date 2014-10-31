# encoding: utf8
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from marketing.models import SiteData
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_p2p.amortization_plan import get_amortization_plan
from wanglibao_p2p.forms import PurchaseForm
from wanglibao_p2p.keeper import ProductKeeper
from wanglibao_p2p.models import P2PProduct, P2PEquity, P2PRecord, Earning
from wanglibao_p2p.serializers import P2PProductSerializer
from wanglibao_p2p.trade import P2PTrader
from wanglibao.const import ErrorNumber
from wanglibao_sms.utils import validate_validation_code
from operator import attrgetter, itemgetter
from django.conf import settings
from decimal import Decimal
from hashlib import md5
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_p2p.utility import strip_tags
from wanglibao_announcement.utility import AnnouncementP2P
from wanglibao_account.models import Binding

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
                                                               p2p.expected_earning_rate/100,
                                                               p2p.amortization_count,
                                                               p2p.period)
        total_earning = terms.get("total") - p2p.total_amount

        total_fee_earning = 0

        if p2p.activity:
            total_fee_earning = Decimal(p2p.total_amount*p2p.activity.rule.rule_amount*(Decimal(p2p.period)/Decimal(12))).quantize(Decimal('0.01'))

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
        phone = request.user.wanglibaouserprofile.phone
        code = request.POST.get('validate_code', '')
        # status_code, message = validate_validation_code(phone, code)
        # if status_code != 200:
        #     return Response({
        #         'message': u'验证码输入错误',
        #         'error_number': ErrorNumber.validate_code_wrong
        #     }, status=status.HTTP_400_BAD_REQUEST)
        if form.is_valid():
            p2p = form.cleaned_data['product']
            amount = form.cleaned_data['amount']

            try:
                trader = P2PTrader(product=p2p, user=request.user)
                product_info, margin_info, equity_info = trader.purchase(amount)
                print product_info, '####'
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
        # code = request.POST.get('validate_code', '')
        # status_code, message = validate_validation_code(phone, code)
        #
        # if status_code != 200:
        #     return Response({
        #         'message': u'验证码输入错误',
        #         'error_number': ErrorNumber.validate_code_wrong
        #     }, status=status.HTTP_200_OK)
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


        return HttpResponseRedirect('/'+settings.ADMIN_ADDRESS+'/wanglibao_p2p/p2pproduct/')


audit_product_view = staff_member_required(AuditProductView.as_view())



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


class P2PProductListView(generics.ListCreateAPIView):

    model = P2PProduct
    permission_classes = IsAdminUserOrReadOnly,
    serializer_class = P2PProductSerializer


    def get_queryset(self):

        maxid = self.request.QUERY_PARAMS.get('maxid', '')
        minid = self.request.QUERY_PARAMS.get('minid', '')

        pager = None
        if maxid and not minid:
            pager = Q(id__gt=maxid)
        if minid and not maxid:
            pager = Q(id__lt=minid)

        if pager:
            return  P2PProduct.objects.filter(hide=False).filter(status__in=[
                    u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标'
                ]).filter(pager).order_by('-priority')
        else:
            return P2PProduct.objects.filter(hide=False).filter(status__in=[
                    u'已完成', u'满标待打款', u'满标已打款', u'满标待审核', u'满标已审核', u'还款中', u'正在招标'
                ]).order_by('-priority')


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
            u'还款中', u'已完成'
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


class FinancesAPI(APIView):
    permission_classes = (IsAdminUserOrReadOnly,)

    def get(self, request):

        p2pproducts = P2PProduct.objects.filter(hide=False).filter(status__in=[
            u'正在招标', u'还款中', u'已完成'
        ])

        p2p_list = []
        status = 0
        for p2p in p2pproducts:
            shouyi = "{}%".format(p2p.expected_earning_rate)
            if p2p.status == u'正在招标':
                status = 1

            temp_p2p = {
                "logo": "https://{}/static/images/wlblogo.png".format(self.request.get_host()),
                "link": "https://{}/p2p/detail/{}/?promo_token=TL86KmhJShuqyBO0ZxR17A".format(self.request.get_host(), p2p.id),
                "chanpin": p2p.name,
                "serial": "WLB{}{}".format(timezone.localtime(p2p.publish_time).strftime("%Y%m%d%H%M%S"), p2p.id),
                "xinyong": u'全额本息担保',
                "touzi": "{}元".format(p2p.total_amount),
                "shouyi": shouyi,
                "touzi_time": "{}月".format(p2p.period),
                "status": status
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

        equities = product.p2precord_set.filter(catalog=u'申购').prefetch_related('user').prefetch_related('user__wanglibaouserprofile')

        record = [{
           "amount": float(eq.amount),
            "user": eq.user.wanglibaouserprofile.phone,
            "create_time": timezone.localtime(eq.create_time).strftime("%Y-%m-%d %H:%M:%S")
        } for eq in equities]

        return Response(record)


class P2PListView(TemplateView):
    template_name = 'p2p_list.jade'

    def get_context_data(self, **kwargs):

        p2p_done = P2PProduct.objects.select_related('warrant_company', 'activity').filter(hide=False).filter(Q(publish_time__lte=timezone.now()))\
            .filter(status= u'正在招标').order_by('-publish_time')
        print p2p_done
        p2p_others = P2PProduct.objects.select_related('warrant_company', 'activity').filter(hide=False).filter(Q(publish_time__lte=timezone.now())).filter(
            status__in=[
                u'已完成', u'满标待打款',u'满标已打款', u'满标待审核', u'满标已审核', u'还款中'
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


