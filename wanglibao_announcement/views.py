# encoding: utf8
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import TemplateView
from wanglibao_announcement.models import Announcement


class AnnouncementView(TemplateView):
    template_name = 'announcement_list.jade'

    def get_context_data(self, **kwargs):
        Announcements = Announcement

        return Announcements