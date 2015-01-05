# encoding:utf8
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_banner.filter import BannerFilterSet
from wanglibao_banner.models import Banner, Hiring
from wanglibao_banner.serializer import BannerSerializer
from django.views.generic import TemplateView


class BannerViewSet(PaginatedModelViewSet):
    """
    广告条
    """
    model = Banner
    serializer_class = BannerSerializer
    filter_class = BannerFilterSet
    permission_classes = (IsAdminUserOrReadOnly,)


class HiringView(TemplateView):
    template_name = 'hiring.jade'

    def get_context_data(self, **kwargs):

        hiring = Hiring.objects.filter(is_hide=False).order_by('-priority')

        return {
            'hirings': hiring
        }

