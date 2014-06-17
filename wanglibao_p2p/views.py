# encoding: utf8

from django.http import Http404
from django.utils import timezone
from django.views.generic import TemplateView
from wanglibao_p2p.forms import PurchaseForm
from wanglibao_p2p.models import P2PProduct


class P2PDetailView(TemplateView):
    template_name = "p2p_detail.jade"

    def get_context_data(self, id, **kwargs):
        status = 'finished'

        try:
            p2p = P2PProduct.objects.get(pk=id)
            form = PurchaseForm()
            if p2p.remain == 0:
                status = 'finished'
            else:
                if p2p.publish_time <= timezone.now() < p2p.end_time:
                    status = 'open'
                elif timezone.now() > p2p.end_time:
                    status = 'finished'

        except P2PProduct.DoesNotExist:
            raise Http404(u'您查找的产品不存在')

        return {
            'p2p': p2p,
            'form': form,
            'status': status
        }
