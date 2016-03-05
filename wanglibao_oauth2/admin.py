from django.contrib import admin
from .models import AccessToken, Client, RefreshToken, OauthUser


class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'client', 'token', 'expires',)
    raw_id_fields = ('user',)


class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'client', 'token', 'access_token', 'expired',)
    raw_id_fields = ('user',)


class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_id', 'channel', 'created_time')
    raw_id_fields = ('channel',)


class OauthUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'client', 'created_time')
    raw_id_fields = ('user',)

admin.site.register(AccessToken, AccessTokenAdmin)
admin.site.register(RefreshToken, RefreshTokenAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(OauthUser, OauthUserAdmin)
