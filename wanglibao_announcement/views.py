# encoding: utf8

from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from wanglibao_announcement.models import Announcement, AppMemorabilia
from django.utils import timezone


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


class AppMemorabiliaHomeView(TemplateView):
    template_name = 'app_memorabilia_home.jade'

    def get_context_data(self, **kwargs):
        memorabilia = AppMemorabilia.objects.filter(hide_link=False,
                                                    start_time__lte=timezone.now()).order_by('-priority')

        memorabilia_list = []
        memorabilia_list.extend(memorabilia)

        limit = 10
        paginator = Paginator(memorabilia_list, limit)
        page = self.request.GET.get('page')

        try:
            memorabilia_list = paginator.page(page)
        except PageNotAnInteger:
            memorabilia_list = paginator.page(1)
        except Exception:
            memorabilia_list = paginator.page(paginator.num_pages)

        return {
            'announcements': memorabilia_list
        }


class AppMemorabiliaDetailView(TemplateView):
    template_name = 'memorabilia_detail.jade'

    def get_context_data(self, id, **kwargs):
        context = super(AppMemorabiliaDetailView, self).get_context_data(**kwargs)

        try:
            memorabilia = (AppMemorabilia.objects.get(pk=id,
                                                      hide_link=False,
                                                      start_time__lte=timezone.now()))

        except AppMemorabilia.DoesNotExist:
            raise Http404(u'您查找的大事记不存在')

        context.update({
            'memorabilia': memorabilia,

        })

        return context


class AppMemorabiliaPreviewView(TemplateView):
    template_name = 'app_memorabilia_preview.jade'

    def get_context_data(self, id, **kwargs):
        context = super(AppMemorabiliaPreviewView, self).get_context_data(**kwargs)

        try:
            memorabilia = AppMemorabilia.objects.get(pk=id)

        except AppMemorabilia.DoesNotExist:
            raise Http404(u'您查找的大事记不存在')

        context.update({
            'memorabilia': memorabilia,

        })

        return context
