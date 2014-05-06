from django.views.generic import TemplateView
from wanglibao_hotlist.models import HotTrust, HotFund, HotFinancing


class IndexView(TemplateView):
    template_name = 'index.jade'

    def get_context_data(self, **kwargs):
        count = 4

        hot_trusts = HotTrust.objects.all().prefetch_related('trust').\
                         prefetch_related('trust__issuer')[:count]
        hot_funds = HotFund.objects.all().prefetch_related('fund').\
                        prefetch_related('fund__issuer')[:count]
        hot_financings = HotFinancing.objects.all().prefetch_related('bank_financing').\
                             prefetch_related('bank_financing__bank')[:count]

        return {
            'hot_trusts': hot_trusts,
            'hot_funds': hot_funds,
            'hot_financings': hot_financings
            }

