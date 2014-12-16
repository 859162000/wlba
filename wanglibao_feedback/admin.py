from django.contrib import admin
from wanglibao_feedback.models import Feedback

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by')
    raw_id_fields = ('created_by', )

admin.site.register(Feedback, FeedbackAdmin)
