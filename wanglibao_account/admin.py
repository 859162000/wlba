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
from wanglibao_account.models import VerifyCounter, IdVerification, Binding, Message, MessageText, UserPushId, UserAddress
from wanglibao_margin.models import Margin
from wanglibao_p2p.models import P2PEquity
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_account.views import AdminIdVerificationView, IntroduceRelation, AdminSendMessageView
from wanglibao.templatetags.formatters import safe_phone_str, safe_name
from django.forms.models import BaseInlineFormSet


class ProfileInline(admin.StackedInline):
    model = WanglibaoUserProfile
    readonly_fields = ('deposit_default_bank_name',)

    def has_delete_permission(self, request, obj=None):
        return False


class MarginInline(admin.StackedInline):
    model = Margin
    readonly_fields = ('margin', 'freeze', 'withdrawing', 'invest')

    def has_delete_permission(self, request, obj=None):
        return False


class P2PEquityFormSet(BaseInlineFormSet):

    def get_queryset(self):
        query_set = super(P2PEquityFormSet, self).get_queryset().order_by('-created_at')
        return query_set[:10]


class P2PEquityInline(admin.StackedInline):
    model = P2PEquity
    extra = 0
    raw_id_fields = ('product',)
    readonly_fields = ('product', 'equity', 'confirm', 'confirm_at', 'contract', 'created_at')
    formset = P2PEquityFormSet
    verbose_name_plural = u'用户持仓（最近10条）'

    def has_delete_permission(self, request, obj=None):
        return False


class PromotionTokenInline(admin.StackedInline):
    model = PromotionToken
    readonly_fields = ('token',)

    def has_delete_permission(self, request, obj=None):
        return False


class UserResource(resources.ModelResource):
    margin = fields.Field(attribute="margin__margin", widget=DecimalWidget())

    phone = fields.Field(attribute="wanglibaouserprofile__phone")
    name = fields.Field(attribute="wanglibaouserprofile__name")

    class Meta:
        model = User
        fields = ('id', 'phone', 'name', 'joined_date')


class UserProfileAdmin(ReadPermissionModelAdmin, UserAdmin):
    actions = None
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

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


def user_unicode(self):
    if hasattr(self, 'wanglibaouserprofile'):
        return u'[%s] %s %s ' % (str(self.id), self.wanglibaouserprofile.name, self.wanglibaouserprofile.phone)
    else:
        return u'%s [%s]' % (str(self.id), self.username)

User.__unicode__ = user_unicode


class IdVerificationAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'name', 'id_number', 'is_valid', 'created_at')
    search_fields = ('name', 'id_number')
    list_filter = ('is_valid', )

    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('wanglibao_account.view_idverification'):
            return ( 'name', 'id_number', 'is_valid', 'created_at')
        return ()

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class VerifyCounterAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('id', 'user', 'count')
    raw_id_fields = ('user',)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('wanglibao_account.view_verifycounter'):
            return ( 'user', 'count')
        return ()

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class UserPushIdAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("user", "device_type", "push_user_id", "push_channel_id")
    raw_id_fields = ('user', )
    search_fields = ('user__wanglibaouserprofile__phone',)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class BindingAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("user", "bid", "btype", "isvip")
    search_fields = ('user__wanglibaouserprofile__phone',)
    raw_id_fields = ('user', )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class MessageAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("id", "target_user", "message_text", "read_status", "format_read_at")
    raw_id_fields = ('target_user', 'message_text')
    search_fields = ('target_user__wanglibaouserprofile__phone',)

    def format_read_at(self, obj):
        return datetime.datetime.fromtimestamp(obj.read_at)
    format_read_at.short_description = u"查看时间"

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return self.raw_id_fields


class MessageTextAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("id", "mtype", "title", "content")
    list_filter = ('mtype', )
    # search_fields = ('content', )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return self.list_display


class UserAddressAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("id", "name", "phone_number", "address", "province", "city", "area", "postcode", "is_default")
    search_fields = ('user__wanglibaouserprofile__phone', 'phone_number')
    raw_id_fields = ('user', )

    def has_add_permission(self, request):
        return False


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
admin.site.register(UserAddress, UserAddressAdmin)

admin.site.register_view('accounts/message/', view=AdminSendMessageView.as_view(), name=u'网利宝-发送站内信')
