from django.contrib import admin
from wanglibao_announcement.models import Announcement


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'device', 'type', 'starttime', 'endtime', 'priority', 'status')

admin.site.register(Announcement, AnnouncementAdmin)