# encoding:utf-8
from django.contrib import admin
from .models import Account
from django.core.urlresolvers import reverse


class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'classify', 'weixin_connect_url', 'weixin_connect_token', 'manage_url')
    search_fields = ('name',)
    fields = ('name', 'classify', 'app_id', 'app_secret')

    def weixin_connect_url(self, obj):
        return 'http://wx.pythink.com/wx/connect/%s/' % obj.id

    weixin_connect_url.short_description = u'微信接口配置URL'

    def weixin_connect_token(self, obj):
        return '%s' % obj.token

    weixin_connect_token.short_description = u'微信接口配置Token'

    def manage_url(self, obj):
        url = reverse('weixin_manage', kwargs={'id': obj.id})
        return '<a href="{url}">管理</a>'.format(url=url)

    manage_url.short_description = u'操作'
    manage_url.allow_tags = True

admin.site.register(Account, AccountAdmin)
