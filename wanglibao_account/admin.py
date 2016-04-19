# coding=utf-8

from django.contrib import admin
from django.contrib.auth.models import User
from wanglibao_account.models import Binding


def user_unicode(self):
    if hasattr(self, 'wanglibaouserprofile'):
        return u'[%s] %s ' % (str(self.id), self.wanglibaouserprofile.phone)
    else:
        return u'%s [%s]' % (str(self.id), self.username)

User.__unicode__ = user_unicode


class BindingAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("user", "bid", "channel")
    search_fields = ('user__wanglibaouserprofile__phone',)
    raw_id_fields = ('user', )
    model = Binding

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


admin.site.register(Binding, BindingAdmin)
