from django.contrib import admin
from wanglibao_feedback.models import Feedback
import datetime
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('created_by', 'Content', 'one_line_created_at')
    raw_id_fields = ('created_by', )

    def Content(self, obj):
        content = obj.content[:140]
        if len(content) == 140:
            content = content + '...'

        return content

admin.site.register(Feedback, FeedbackAdmin)
