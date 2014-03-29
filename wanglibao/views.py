from django.views.generic import TemplateView
from wanglibao_hotlist.models import HotTrust, HotFund, HotFinancing


class IndexView(TemplateView):
    template_name = 'index.jade'

    def get_context_data(self, **kwargs):
        hot_trusts = HotTrust.objects.all()[:6]
        hot_funds = HotFund.objects.all()[:6]
        hot_financings = HotFinancing.objects.all()[:6]

        return {
            'hot_trusts': hot_trusts,
            'hot_funds': hot_funds,
            'hot_financings': hot_financings
            }
