# coding=utf-8
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import DecimalWidget
from marketing.models import PromotionToken, IntroducedBy
from wanglibao_account.models import VerifyCounter, IdVerification
from wanglibao_margin.models import Margin
from wanglibao_p2p.models import P2PEquity
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_account.views import AdminIdVerificationView

class ProfileInline(admin.StackedInline):
    model = WanglibaoUserProfile


class MarginInline(admin.StackedInline):
    model = Margin


class P2PEquityInline(admin.StackedInline):
    model = P2PEquity
    extra = 0


class PromotionTokenInline(admin.StackedInline):
    model = PromotionToken


class UserResource(resources.ModelResource):
    margin = fields.Field(attribute="margin__margin", widget=DecimalWidget())

    phone = fields.Field(attribute="wanglibaouserprofile__phone")
    name = fields.Field(attribute="wanglibaouserprofile__name")

    class Meta:
        model = User
        fields = ('id', 'phone', 'name', 'joined_date')


class UserProfileAdmin(UserAdmin, ImportExportModelAdmin):
    inlines = [ProfileInline, MarginInline, PromotionTokenInline, P2PEquityInline]
    list_display = ('id', 'username', 'phone', 'name', 'id_num', 'is_active', 'date_joined', 'is_staff')
    list_display_links = ('id', 'username', 'phone')
    search_fields = ['wanglibaouserprofile__phone', 'wanglibaouserprofile__id_number', 'wanglibaouserprofile__name']
    resource_class = UserResource

    def phone(self, obj):
        return "%s" % obj.wanglibaouserprofile.phone
    phone.short_description = u'电话'

    def name(self, obj):
        return "%s" % obj.wanglibaouserprofile.name
    name.short_description = u'姓名'

    def id_num(self, obj):
        return obj.wanglibaouserprofile.id_number
    id_num.short_description = u'身份证'


def user_unicode(self):
    if hasattr(self, 'wanglibaouserprofile'):
        return u'[%s] %s %s ' % (str(self.id), self.wanglibaouserprofile.name, self.wanglibaouserprofile.phone)
    else:
        return u'%s [%s]' % (str(self.id), self.username)

User.__unicode__ = user_unicode

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
admin.site.register(IdVerification)
admin.site.register(VerifyCounter)
admin.site.register_view('accounts/id_verify/', view=AdminIdVerificationView.as_view(), name=u'网利宝-身份验证')