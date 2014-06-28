# coding=utf-8
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from wanglibao_margin.models import Margin
from wanglibao_p2p.models import P2PEquity
from wanglibao_profile.models import WanglibaoUserProfile


class ProfileInline(admin.StackedInline):
    model = WanglibaoUserProfile


class MarginInline(admin.StackedInline):
    model = Margin


class P2PEquityInline(admin.StackedInline):
    model = P2PEquity


class UserProfileAdmin(UserAdmin):
    inlines = [ProfileInline, MarginInline, P2PEquityInline]
    list_display = ('phone', 'name', 'id_num', 'is_active', 'date_joined', 'is_staff')

    search_fields = ['wanglibaouserprofile__phone', 'wanglibaouserprofile__id_number', 'wanglibaouserprofile__name']

    def phone(self, obj):
        return "%s" % obj.wanglibaouserprofile.phone
    phone.short_description = u'电话'

    def name(self, obj):
        return "%s" % obj.wanglibaouserprofile.name
    name.short_description = u'姓名'

    def id_num(self, obj):
        return obj.wanglibaouserprofile.id_number
    id_num.short_description = u'身份证'

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)