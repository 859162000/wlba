from django.contrib import admin
from wanglibao_favorite.models import FavoriteTrust, FavoriteFinancing, FavoriteFund, FavoriteCash

class FavoriteTrustAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    raw_id_fields = ('user', 'item')
    search_fields = ('user__wanglibaouserprofile__phone', )


class FavoriteFundAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    raw_id_fields = ('user', 'item')
    search_fields = ('user__wanglibaouserprofile__phone', )


class FavoriteFinancingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    raw_id_fields = ('user', 'item')
    search_fields = ('user__wanglibaouserprofile__phone', )

class FavoriteCashAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    raw_id_fields = ('user', 'item')
    search_fields = ('user__wanglibaouserprofile__phone', )

admin.site.register(FavoriteTrust, FavoriteTrustAdmin)
admin.site.register(FavoriteFund, FavoriteFundAdmin)
admin.site.register(FavoriteFinancing, FavoriteFinancingAdmin)
admin.site.register(FavoriteCash, FavoriteCashAdmin)

