from django.shortcuts import render
from rest_framework import viewsets
from wanglibao_hotlist.models import HotTrust


class HotTrustViewSet(viewsets.ModelViewSet):
    model = HotTrust
