from django.shortcuts import render

from django.views.generic import  TemplateView
from django.db.models import Count
from wanglibao_profile.models import WanglibaoUserProfile
from django.contrib.auth.models import User

# Create your views here.

class MarketingView(TemplateView):
    template_name = 'diary.jade'

    def get_context_data(self, **kwargs):

        all = User.objects.extra({'join_date': 'date(date_joined)'}).values('join_date').annotate(count=Count('id'))

        return {
            'users': all
        }