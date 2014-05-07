from django.contrib import admin
from wanglibao_profile.models import WanglibaoUserProfile


class WanglibaoUserProfileAdmin (admin.ModelAdmin):
    list_display = ('phone', 'nick_name', 'user', 'id_number')

admin.site.register(WanglibaoUserProfile, WanglibaoUserProfileAdmin)

