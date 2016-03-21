# encoding:utf-8

from django.contrib import admin
from wanglibao_feedback.models import Feedback
# import datetime


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'Content', 'created_by', 'created_at')
    raw_id_fields = ('created_by', )
    list_display_links = ('id', 'Content', )

    @staticmethod
    def Content(obj):
        content = obj.content[:140]
        if len(content) == 140:
            content += '...'

        return content

    def get_readonly_fields(self, request, obj=None):
        return self.list_display

admin.site.register(Feedback, FeedbackAdmin)
