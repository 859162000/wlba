from django.views.generic import TemplateView
from wanglibao_hotlist.models import HotTrust, HotFund, HotFinancing

class IndexView(TemplateView):
    template_name = 'index.jade'

    def get_context_data(self, **kwargs):
        count = 4
        hot_trusts = HotTrust.objects.all()[:count]
        hot_funds = HotFund.objects.all()[:count]
        hot_financings = HotFinancing.objects.all()[:count]

        return {
            'hot_trusts': hot_trusts,
            'hot_funds': hot_funds,
            'hot_financings': hot_financings
            }
