from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao_buy.models import BuyInfo
from wanglibao_buy.serializers import BuyInfoSerializer


class BuyInfoViewSet(PaginatedModelViewSet):
    model = BuyInfo
    serializer_class = BuyInfoSerializer
    permission_classes = IsAuthenticated,

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA)

        if serializer.is_valid():
            user = None
            if request.user and request.user.is_authenticated():
                user = request.user

            serializer.object.created_by = user
            serializer.object.save()
            return Response(serializer.data)
        else:
            return Response({
                'message': serializer.errors
            }, status=400)
