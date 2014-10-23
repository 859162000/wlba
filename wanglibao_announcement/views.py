# encoding: utf8
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import TemplateView
from wanglibao_announcement.models import Announcement


class AnnouncementHomeView(TemplateView):
    template_name = 'announcement_home.jade'

    # def get_context_data(self, **kwargs):
    #     Announcements = Announcement
    #
    #     return Announcements


class AnnouncementDetailView(TemplateView):
    template_name = 'announcement_detail.jade'

    # def get_context_data(self, **kwargs):
    #     Announcements = Announcement
    #
    #     return Announcements