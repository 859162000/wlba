from django.shortcuts import render
from rest_framework.viewsets import ViewSet, ModelViewSet
from wanglibao_preorder.models import PreOrder


class PreOrderViewSet(ModelViewSet):
    model = PreOrder
