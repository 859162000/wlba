# encoding: utf-8

from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Sum
from django.http import HttpResponseRedirect
import re

from wanglibao_p2p.models import P2PRecord

from experience_gold.models import ExperienceEventRecord, ExperienceProduct, ExperienceAmortization


class ExperienceGoldView(TemplateView):

    def get_template_names(self):
        template = self.kwargs['template']
        if template not in ('mobile', 'gold', 'account', 'nologin', 'redirect'):
            template_name = "experience_gold.jade"
        elif template == 'mobile':
            template_name = 'app_experience.jade'
        elif template == 'account':
            template_name = 'experience_account.jade'
        elif template == 'redirect':
            template_name = 'experience_redirect.jade'
        else:
            template_name = "experience_gold.jade"

        if template_name == 'experience_gold.jade':
            device_list = ['android', 'iphone']
            try:
                user_agent = self.request.META['HTTP_USER_AGENT']
            except Exception:
                user_agent = 'pc'
            for device in device_list:
                match = re.search(device, user_agent.lower())
                if match and match.group():
                    template_name = 'app_experience.jade'
                    break

        return template_name

    def get_context_data(self, **kwargs):
        context = super(ExperienceGoldView, self).get_context_data(**kwargs)

        user = self.request.user
        now = timezone.now()
        experience_amortization = []
        experience_amount = paid_interest = unpaid_interest = 0
        p2p_record_count = experience_count = experience_all = 0

        experience_product = ExperienceProduct.objects.filter(isvalid=True).first()

        if user.is_authenticated():
            p2p_record_count = P2PRecord.objects.filter(user=user).count()
            experience_count = ExperienceEventRecord.objects.filter(user=user).count()

            # 体验金可用余额
            experience_record = ExperienceEventRecord.objects.filter(user=user, apply=False, event__invalid=False)\
                .filter(event__available_at__lt=now, event__unavailable_at__gt=now).aggregate(Sum('event__amount'))
            if experience_record.get('event__amount__sum'):
                experience_amount = experience_record.get('event__amount__sum')

            # 所有体验金总额
            experience_record_all = ExperienceEventRecord.objects.filter(user=user).aggregate(Sum('event__amount'))
            if experience_record_all.get('event__amount__sum'):
                experience_all = experience_record_all.get('event__amount__sum')

            # 体验标还款计划
            experience_amortization = ExperienceAmortization.objects.filter(user=user)\
                .select_related('product').order_by('-created_time')
            if experience_amortization:
                paid_interest = reduce(lambda x, y: x + y,
                                       [e.interest for e in experience_amortization if e.settled is True], 0)
                unpaid_interest = reduce(lambda x, y: x + y,
                                         [e.interest for e in experience_amortization if e.settled is False], 0)

        total_experience_amount = float(experience_amount) + float(paid_interest) + float(unpaid_interest)

        context.update({
            'experience_amount': experience_amount,
            'product': experience_product,
            'experience_amortization': experience_amortization,
            'total_experience_amount': total_experience_amount,
            'paid_interest': paid_interest,
            'unpaid_interest': unpaid_interest,
            'p2p_record_count': p2p_record_count,
            'experience_count': experience_count,
            'experience_all': experience_all
        })
        return context

    def dispatch(self, request, *args, **kwargs):
        return super(ExperienceGoldView, self).dispatch(request, *args, **kwargs)


# class ExperienceAccountsView(TemplateView):
#     template_name = 'experience_account.jade'
#
#     def get_context_data(self, **kwargs):
#         return {}
