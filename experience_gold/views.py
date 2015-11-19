# encoding: utf-8

from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal

from experience_gold.models import ExperienceEventRecord, ExperienceProduct, ExperienceAmortization


class ExperienceGoldView(TemplateView):
    template_name = "experience_gold.jade"

    def get_context_data(self, **kwargs):

        user = self.request.user
        now = timezone.now()
        experience_amount = 0
        experience_amortization = []

        paid_interest = unpaid_interest = 0

        experience_product = ExperienceProduct.objects.filter(isvalid=True).first()

        if user.is_authenticated():
            experience_record = ExperienceEventRecord.objects.filter(user=user, apply=False, event__invalid=False)\
                .filter(event__available_at__lt=now, event__unavailable_at__gt=now).aggregate(Sum('event__amount'))
            if experience_record.get('event__amount__sum'):
                experience_amount = experience_record.get('event__amount__sum')

            experience_amortization = ExperienceAmortization.objects.filter(user=user).select_related('product')
            if experience_amortization:
                paid_interest = reduce(lambda x, y: x + y,
                                       [e.interest for e in experience_amortization if e.settled is True], 0)
                unpaid_interest = reduce(lambda x, y: x + y,
                                         [e.interest for e in experience_amortization if e.settled is False], 0)

        total_experience_amount = float(experience_amount) + float(paid_interest) + float(unpaid_interest)
        return {
            'experience_amount': experience_amount,
            'product': experience_product,
            'experience_amortization': experience_amortization,
            'total_experience_amount': total_experience_amount,
            'paid_interest': paid_interest,
            'unpaid_interest': unpaid_interest
        }
