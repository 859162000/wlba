from django.contrib import admin
from .models import AccessToken, Client, RefreshToken


class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'client', 'token', 'expires',)
    raw_id_fields = ('user',)


class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'access_token', 'expired',)
    raw_id_fields = ('user',)


class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'channel',)
    raw_id_fields = ('channel',)

admin.site.register(AccessToken, AccessTokenAdmin)
admin.site.register(RefreshToken, RefreshTokenAdmin)
admin.site.register(Client, ClientAdmin)
