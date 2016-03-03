# encoding: utf8

from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.views import APIView
from rest_framework.response import Response
from wanglibao_announcement.models import Announcement
from django.utils import timezone
import re
import json


class AnnouncementHomeView(TemplateView):
    template_name = 'announcement_home.jade'

    def get_context_data(self, **kwargs):
        announcements = Announcement.objects.filter(status=1, device='pc', hideinlist=False).order_by('-createtime')

        announcements_list = []
        announcements_list.extend(announcements)

        limit = 10
        paginator = Paginator(announcements_list, limit)
        page = self.request.GET.get('page')

        try:
            announcements_list = paginator.page(page)
        except PageNotAnInteger:
            announcements_list = paginator.page(1)
        except Exception:
            announcements_list = paginator.page(paginator.num_pages)

        return {
            'announcements': announcements_list
        }


class AnnouncementDetailView(TemplateView):
    template_name = 'announcement_detail.jade'

    def get_context_data(self, id, **kwargs):
        context = super(AnnouncementDetailView, self).get_context_data(**kwargs)

        device_list = ['android', 'iphone']
        user_agent = self.request.META.get('HTTP_USER_AGENT', "").lower()
        for device in device_list:
            match = re.search(device, user_agent)
            if match and match.group():
                self.template_name = 'client_announcement_detail.jade'

        try:
            announce = Announcement.objects.get(pk=id, status=1, device='pc')

        except Announcement.DoesNotExist:
            raise Http404(u'您查找的公告不存在')

        context.update({
            'announce': announce,

        })

        return context


class AnnouncementPreviewView(TemplateView):
    template_name = 'announcement_preview.jade'

    def get_context_data(self, id, **kwargs):
        context = super(AnnouncementPreviewView, self).get_context_data(**kwargs)

        try:
            announce = Announcement.objects.get(pk=id)

        except Announcement.DoesNotExist:
            raise Http404(u'您查找的公告不存在')

        context.update({
            'announce': announce,

        })

        return context


class AnnouncementHomeApi(APIView):
    permission_classes = ()

    def post(self, request):
        req_data = request.POST
        device_type = req_data.get('device_type')
        page = int(req_data.get('page', 1))
        page_size = int(req_data.get('page_size', 10))

        announcements = Announcement.objects.filter(Q(status=1, hideinlist=False,) & (Q(device=device_type) | Q(device='pc&app'))
                                                    ).order_by('-createtime').values('id', 'title',
                                                                                     'content', 'createtime')
        if announcements:
            paginator = Paginator(announcements, page_size)
            try:
                announcements = paginator.page(page)
            except PageNotAnInteger:
                announcements = paginator.page(1)
            except EmptyPage:
                announcements = []
            except Exception:
                announcements = paginator.page(paginator.num_pages)

            count = paginator.num_pages
        else:
            announcements = []
            count = 0

        announcements_list = []
        for announce in announcements:
            announce["createtime"] = timezone.localtime(announce["createtime"]).strftime('%Y-%m-%d')
            announcements_list.append(announce)

        return Response({'ret_code': 0, 'data': announcements_list, 'page': page, 'num': page_size, 'count': count})


class AnnouncementHasNewestApi(APIView):
    permission_classes = ()

    def get(self, request, id):
        req_data = request.GET
        device_type = req_data.get('device_type')
        announcements = Announcement.objects.filter(Q(pk__gt=id, status=1, hideinlist=False, device=device_type) |
                                                    Q(pk__gt=id, status=1, hideinlist=False, device='pc&app'))

        result = 1 if announcements.exists() else 0

        return Response({'ret_code': 0, 'result': result})
