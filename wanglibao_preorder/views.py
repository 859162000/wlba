from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.viewsets import ViewSet, ModelViewSet
from wanglibao_preorder.models import PreOrder
from wanglibao_preorder.serializers import PreOrderSerializer


class PreOrderViewSet(ViewSet):
    model = PreOrder
    serializer = PreOrderSerializer
    throttle_classes = (UserRateThrottle,)

    @property
    def allowed_methods(self):
        return 'POST',

    @csrf_exempt
    def create(self, request):
        serializer = self.serializer(data=request.DATA)

        if serializer.is_valid():
            serializer.object.save()
            return Response(serializer.data)
        else:
            return Response({
                'message':'failed'
            }, status=400)
