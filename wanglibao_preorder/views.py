from django.contrib.auth.models import AnonymousUser
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.viewsets import ViewSet

from wanglibao_preorder.models import PreOrder
from wanglibao_preorder.serializers import PreOrderSerializer


class PreOrderViewSet(ViewSet):
    model = PreOrder
    serializer = PreOrderSerializer
    throttle_classes = (UserRateThrottle,)
    permission_classes = (AllowAny,)

    @property
    def allowed_methods(self):
        return 'POST',

    @csrf_exempt
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
