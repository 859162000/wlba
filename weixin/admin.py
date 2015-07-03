# encoding:utf-8
from django.contrib import admin
from .models import Account
from django.core.urlresolvers import reverse
from django.conf import settings


class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'classify', 'connect_url', 'connect_token', 'oauth_login_url', 'manage_url')
    search_fields = ('name',)
    fields = ('name', 'classify', 'app_id', 'app_secret')

    def connect_token(self, obj):
        return '%s' % obj.token

    def manage_url(self, obj):
        url = reverse('admin_weixin_manage', kwargs={'id': obj.id})
        return '<a href="{url}">管理</a>'.format(url=url)

    def connect_url(self, obj):
        pass

    def oauth_login_url(self, obj):
        pass

    connect_token.short_description = u'微信接口配置Token'
    manage_url.short_description = u'操作'
    manage_url.allow_tags = True

    def get_list_display(self, request):
        def replace_url(url):
            if url.startswith('http://') and settings.ENV != settings.ENV_DEV:
                url = url.replace('http://', 'https://')
            return url

        # def connect_url(obj):
        #     url = request.build_absolute_uri(reverse('weixin_connect', kwargs={'id': obj.id}))
        #     return replace_url(url)

        # self.connect_url = connect_url
        # self.connect_url.short_description = u'微信接口配置URL'

        def oauth_login_url(obj):
            url = request.build_absolute_uri(reverse('weixin_oauth_login_redirect'))
            return replace_url(url)

        self.oauth_login_url = oauth_login_url
        self.oauth_login_url.short_description = u'微信登录链接'
        return super(AccountAdmin, self).get_list_display(request)


admin.site.register(Account, AccountAdmin)
