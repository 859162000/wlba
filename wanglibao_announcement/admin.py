from django.contrib import admin
from wanglibao_announcement.models import Announcement, AppMemorabilia


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'device', 'type', 'starttime', 'endtime', 'priority', 'status', 'preview_link', 'createtime')
    list_editable = ('type', 'priority', 'status')
    list_filter = ('device', 'type', 'status')


class AppMemorabiliaAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'detail_link', 'done_date', 'priority')
    # list_editable = ('type', 'priority', 'status')
    # list_filter = ('device', 'type', 'status')

admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(AppMemorabilia, AppMemorabiliaAdmin)
