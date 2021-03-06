from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from trust.models import Trust
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_bank_financing.models import BankFinancing
from wanglibao_cash.models import Cash
from wanglibao_favorite.models import FavoriteTrust, FavoriteFinancing, FavoriteFund, FavoriteCash
from wanglibao_favorite.serializers import FavoriteTrustSerializer, FavoriteFinancingSerializer, FavoriteFundSerializer, \
    FavoriteCashSerializer
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

    def destroy(self, request, pk):
        user = request.user
        self.model.objects.filter(item__id=pk, user=user).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


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


class FavoriteCashViewSet(BaseFavoriteViewSet):
    model = FavoriteCash
    product_model = Cash
    serializer_class = FavoriteCashSerializer

