from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from trust.models import Trust
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_bank_financing.models import BankFinancing
from wanglibao_favorite.models import FavoriteTrust, FavoriteFinancing, FavoriteFund
from wanglibao_favorite.serializers import FavoriteTrustSerializer, FavoriteFinancingSerializer, FavoriteFundSerializer
from wanglibao_fund.models import Fund


class BaseFavoriteViewSet(PaginatedModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = super(BaseFavoriteViewSet, self).get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs

    def create(self, request, *args, **kwargs):
        user = request.user
        item_id = request.DATA['item']
        item = self.product_model.objects.get(pk=item_id)

        if self.model.objects.filter(user=user, item=item).exists():
            return Response(
                {
                    'message': 'Already in user favorite list'
                },
                status=409
            )

        fav_item = self.model()
        fav_item.item = item
        fav_item.user = user
        fav_item.save()

        serializer = self.serializer_class(fav_item)
        return Response(serializer.data)


class FavoriteTrustViewSet(BaseFavoriteViewSet):
    model = FavoriteTrust
    product_model = Trust
    serializer_class = FavoriteTrustSerializer


class FavoriteFinancingViewSet(BaseFavoriteViewSet):
    model = FavoriteFinancing
    product_model = BankFinancing
    serializer_class = FavoriteFinancingSerializer


class FavoriteFundViewSet(BaseFavoriteViewSet):
    model = FavoriteFund
    product_model = Fund
    serializer_class = FavoriteFundSerializer
