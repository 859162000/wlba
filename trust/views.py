from django.db.models import Q
from django.views.generic import TemplateView
from trust.models import Trust


class TrustHomeView(TemplateView):

    template_name = "trust_home.html"

    def get_context_data(self, **kwargs):
        context = super(TrustHomeView, self).get_context_data(**kwargs)

        latest_trusts = Trust.objects.order_by('-issue_date')[0:10] # TODO make this value configurable
        context['latest_trusts'] = latest_trusts
