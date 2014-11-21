# encoding: utf8
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from wanglibao_announcement.models import Announcement


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