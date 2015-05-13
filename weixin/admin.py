# encoding:utf-8
from django.contrib import admin
from .models import Account
from django.core.urlresolvers import reverse


class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'classify', 'weixin_connect_url', 'weixin_connect_token', 'manage_url')
    search_fields = ('name',)
    fields = ('name', 'classify', 'app_id', 'app_secret')

    def get_list_display(self, request):
        def weixin_connect_url(obj):
            return request.build_absolute_uri(reverse('weixin_connect', kwargs={'id': obj.id}))
        self.weixin_connect_url = weixin_connect_url
        return super(AccountAdmin, self).get_list_display(request)

    def weixin_connect_token(self, obj):
        return '%s' % obj.token

    def manage_url(self, obj):
        url = reverse('admin_weixin_manage', kwargs={'id': obj.id})
        return '<a href="{url}">管理</a>'.format(url=url)

    def weixin_connect_url(self, obj):
        pass

    weixin_connect_token.short_description = u'微信接口配置Token'
    weixin_connect_url.short_description = u'微信接口配置URL'
    manage_url.short_description = u'操作'
    manage_url.allow_tags = True

admin.site.register(Account, AccountAdmin)
