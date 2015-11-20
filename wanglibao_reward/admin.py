from django.contrib import admin
from wanglibao_reward.models import WanglibaoActivityGift, WanglibaoUserGift, WanglibaoActivityGiftGlobalCfg, \
    WanglibaoWeixinRelative, WanglibaoActivityReward

class WanglibaoActivityGiftGlobalCfgAdmin(admin.ModelAdmin):

    action = None
    list_display = ('activity', 'chances', 'when_register', 'terminal_type', 'amount')


class WanglibaoActivityGiftAdmin(admin.ModelAdmin):
    """
       add by yihen@20150901
    """

    action = None
    list_display = ("gift_id", "activity", "redpack", "cfg", "type", "chances", "name", "rate", "send_rate", "total_count", "each_day_count", "channels", "valid",)



class WanglibaoUserGiftAdmin(admin.ModelAdmin):


    action = None
    list_display = ("activity", "user", "rules", "identity", "index", "type", "name", "valid", "amount")


class WanglibaoWeixinRelativeAdmin(admin.ModelAdmin):
    action = None
    list_display = ("user", "phone", "nick_name", "openid", "img",)


class WanglibaoActivityRewardAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("activity", "when_dist", "left_times", "join_times", "redpack_event", "user", "channel", "p2p_amount", "create_at", "update_at",)

admin.site.register(WanglibaoActivityReward, WanglibaoActivityRewardAdmin)
admin.site.register(WanglibaoWeixinRelative, WanglibaoWeixinRelativeAdmin)
admin.site.register(WanglibaoActivityGiftGlobalCfg, WanglibaoActivityGiftGlobalCfgAdmin)
admin.site.register(WanglibaoUserGift, WanglibaoUserGiftAdmin)
admin.site.register(WanglibaoActivityGift, WanglibaoActivityGiftAdmin)

