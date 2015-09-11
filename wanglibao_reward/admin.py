from django.contrib import admin
from wanglibao_reward.models import WanglibaoActivityGift, WanglibaoUserGift
# Register your models here.class WanglibaoGiftAdmin(admin.ModelAdmin):

class WanglibaoGiftAdmin(admin.ModelAdmin):
    """
       add by yihen@20150901
    """
    action = None
    list_display = ('type', 'name', 'code', 'rate', 'activity', 'count', 'channels', 'valid')


class WanglibaoUserGiftAdmin(admin.ModelAdmin):
    action = None
    list_display = ('activity', 'index', 'name', 'valid')


admin.site.register(WanglibaoUserGift, WanglibaoUserGiftAdmin)
admin.site.register(WanglibaoActivityGift, WanglibaoGiftAdmin)

