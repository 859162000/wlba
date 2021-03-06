from django.http import Http404
from django.views.generic import TemplateView
from trust.filters import TrustFilterSet
from trust.models import Trust, Issuer
from serializers import TrustSerializer
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_favorite.models import FavoriteTrust
from wanglibao_hotlist.models import HotTrust
from wanglibao_announcement.utility import AnnouncementTrust


class TrustHomeView(TemplateView):

    template_name = "trust_home.jade"

    def get_context_data(self, **kwargs):
        hot_trusts = HotTrust.objects.all().prefetch_related('trust').prefetch_related('trust__issuer')[:3]

        return {
            'hot_trusts': hot_trusts,
            'announcements': AnnouncementTrust
        }


class TrustDetailView(TemplateView):
    template_name = "trust_detail.jade"

    def get_context_data(self, **kwargs):
        id = kwargs['id']
        context = super(TrustDetailView, self).get_context_data(**kwargs)
        try:
            trust = Trust.objects.get(pk=id)
        except Trust.DoesNotExist, e:
            raise Http404

        context['trust'] = trust
        is_favorited = 0
        if self.request.user.is_authenticated():
            if FavoriteTrust.objects.filter(user=self.request.user, item=trust).exists():
                is_favorited = 1
        context['is_favorited'] = is_favorited

        context['announcements'] = AnnouncementTrust

        return context


class TrustViewSet(PaginatedModelViewSet):
    model = Trust
    filter_class = TrustFilterSet
    serializer_class = TrustSerializer
    permission_classes = (IsAdminUserOrReadOnly,)

    def get_queryset(self):
        return Trust.objects.all().prefetch_related('issuer')


class IssuerViewSet(PaginatedModelViewSet):
    model = Issuer
    permission_classes = (IsAdminUserOrReadOnly,)
