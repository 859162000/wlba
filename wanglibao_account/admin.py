# coding=utf-8

import datetime
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import DecimalWidget
from marketing.models import PromotionToken, IntroducedBy
from wanglibao.admin import ReadPermissionModelAdmin
from wanglibao_account.models import VerifyCounter, IdVerification, Binding, Message, MessageText, UserPushId
from wanglibao_margin.models import Margin
from wanglibao_p2p.models import P2PEquity
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_account.views import AdminIdVerificationView, IntroduceRelation, AdminSendMessageView


class ProfileInline(admin.StackedInline):
    model = WanglibaoUserProfile


class MarginInline(admin.StackedInline):
    model = Margin
    readonly_fields = ('margin', 'freeze', 'withdrawing')


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


class UserProfileAdmin(ReadPermissionModelAdmin, UserAdmin, ImportExportModelAdmin):
    inlines = [ProfileInline, MarginInline, PromotionTokenInline, P2PEquityInline]
    list_display = ('id', 'username', 'phone', 'name', 'utype', 'id_num', 'is_active', 'date_joined', 'is_staff')
    list_display_links = ('id', 'username', 'phone')
    list_filter = ('wanglibaouserprofile__utype', 'is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ['username', 'wanglibaouserprofile__phone', 'wanglibaouserprofile__id_number', 'wanglibaouserprofile__name']
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

    def utype(self, obj):
        return obj.wanglibaouserprofile.utype
    utype.short_description = u'用户类型'

    def get_export_queryset(self, request):
        qs = super(UserProfileAdmin, self).get_queryset(request)
        qs = qs.select_related('user').select_related('wanglibaouserprofile__phone')
        return qs


def user_unicode(self):
    if hasattr(self, 'wanglibaouserprofile'):
        return u'[%s] %s %s ' % (str(self.id), self.wanglibaouserprofile.name, self.wanglibaouserprofile.phone)
    else:
        return u'%s [%s]' % (str(self.id), self.username)

User.__unicode__ = user_unicode


class IdVerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'id_number', 'is_valid', 'created_at')
    search_fields = ('name', 'id_number')
    list_filter = ('is_valid', )

    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('wanglibao_account.view_idverification'):
            return ( 'name', 'id_number', 'is_valid', 'created_at')
        return ()

class VerifyCounterAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'count')

    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('wanglibao_account.view_verifycounter'):
            return ( 'user', 'count')
        return ()

class UserPushIdAdmin(admin.ModelAdmin):
    list_display = ("user", "device_type", "push_user_id", "push_channel_id")
    raw_id_fields = ('user', )
    search_fields = ('user__wanglibaouserprofile__phone',)

class BindingAdmin(admin.ModelAdmin):
    list_display = ("user", "bid", "btype", "isvip")
    search_fields = ('user__wanglibaouserprofile__phone',)
    raw_id_fields = ('user', )

class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "target_user", "message_text", "read_status", "format_read_at")
    raw_id_fields = ('target_user', 'message_text')

    def format_read_at(self, obj):
        return datetime.datetime.fromtimestamp(obj.read_at)
    format_read_at.short_description = u"查看时间"

class MessageTextAdmin(admin.ModelAdmin):
    list_display = ("id", "mtype", "title", "content")
    list_filter = ('mtype', )
    # search_fields = ('content', )


admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
admin.site.register(IdVerification, IdVerificationAdmin)
admin.site.register(VerifyCounter, VerifyCounterAdmin)
admin.site.register_view('accounts/id_verify/', view=AdminIdVerificationView.as_view(), name=u'网利宝-身份验证')
admin.site.register_view('accounts/add_introduce/', view=IntroduceRelation.as_view(), name=u'网利宝-新增邀请')
admin.site.register(Binding, BindingAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(MessageText, MessageTextAdmin)
admin.site.register(UserPushId, UserPushIdAdmin)

admin.site.register_view('accounts/message/', view=AdminSendMessageView.as_view(), name=u'网利宝-发送站内信')
