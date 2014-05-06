from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.permissions import AllowAnyPostOnlyAdminList

from wanglibao_preorder.models import PreOrder
from wanglibao_preorder.serializers import PreOrderSerializer


class PreOrderViewSet(PaginatedModelViewSet):
    model = PreOrder
    serializer = PreOrderSerializer
    throttle_classes = (UserRateThrottle,)
    permission_classes = AllowAnyPostOnlyAdminList,

    @property
    def allowed_methods(self):
        return 'POST', 'GET'

    def create(self, request):
        serializer = self.serializer(data=request.DATA)

        if serializer.is_valid():
            user = None
            if request.user and request.user.is_authenticated():
                user = request.user

            serializer.object.user = user
            serializer.object.save()
            return Response(serializer.data)
        else:
            return Response({
                'message': 'failed'
            }, status=400)
