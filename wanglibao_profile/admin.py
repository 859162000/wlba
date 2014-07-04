from django.contrib import admin
from wanglibao_profile.models import WanglibaoUserProfile


class WanglibaoUserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'nick_name', 'id_number')
    search_fields = ('phone', )

admin.site.register(WanglibaoUserProfile, WanglibaoUserProfileAdmin)

