# encoding: utf8

from django.contrib import admin
from django import forms
from wanglibao_announcement.models import Announcement, AppMemorabilia


class AnnouncementForm(forms.ModelForm):
    def clean(self):
        device = self.cleaned_data['device']
        if device in ['mobile', 'pc&app']:
            page_title = self.cleaned_data.get('page_title', None)
            if not page_title:
                raise forms.ValidationError(u"移动端公告『公告页面标题』不能为空")

        return self.cleaned_data

    class Meta:
        forms.model = Announcement


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'device', 'type', 'starttime', 'endtime', 'priority', 'status', 'preview_link', 'createtime')
    list_editable = ('type', 'priority', 'status')
    list_filter = ('device', 'type', 'status')
    form = AnnouncementForm


class AppMemorabiliaAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'detail_link', 'done_date', 'priority')
    search_fields = ('title',)
    fields = ('title', 'banner', 'detail_link', 'done_date', 'priority', 'hide_link',
              'start_time')

    def save_model(self, request, obj, form, change):
        if obj.hide_link is True:
            obj.status = 0

        if obj.hide_link is False:
            obj.status = 1

        obj.save()


admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(AppMemorabilia, AppMemorabiliaAdmin)
