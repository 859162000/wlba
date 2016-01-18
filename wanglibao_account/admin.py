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
from wanglibao_account.models import VerifyCounter, IdVerification, Binding, Message, MessageText, UserPushId, \
                                     UserAddress, UserThreeOrder
from wanglibao_margin.models import Margin
from wanglibao_p2p.models import P2PEquity
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_account.views import AdminIdVerificationView, AdminSendMessageView
from wanglibao.templatetags.formatters import safe_phone_str, safe_name
from django.forms.models import BaseInlineFormSet
from wanglibao_account.models import UserSource
from wanglibao.settings import ENV, ENV_PRODUCTION
from .backends import get_verify_result
from .utils import Xunlei9AdminCallback
from wanglibao_p2p.models import P2PRecord
from wanglibao_pay.models import PayInfo
from .utils import xunleivip_generate_sign
from marketing.utils import get_user_channel_record
from .tasks import xunleivip_callback
from decimal import Decimal
from django.conf import settings
from wanglibao_account.models import UserSource
from wanglibao.settings import ENV, ENV_PRODUCTION
from .backends import get_verify_result


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
    list_display = ('id', 'name', 'id_number', 'is_valid', 'description', 'created_at',)
    search_fields = ('name', 'id_number')
    list_filter = ('is_valid', )

    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('wanglibao_account.view_idverification'):
            return ('name', 'id_number', 'is_valid', 'created_at',)
        return ()

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        if obj.update_verify is True:
            form.update_verify = False
            obj.update_verify = False

            # 只有生产环境可以实现更新操作
            if ENV == ENV_PRODUCTION:
                verify_result, _id_photo, message = get_verify_result(obj.id_number, obj.name)
                obj.description = message
                if verify_result:
                    obj.is_valid = True
                    if _id_photo:
                        obj.id_photo.save('%s.jpg' % obj.id_number, _id_photo, save=True)

        obj.save()


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
    model = Binding

    def xunlei_call_back(self, user, tid, data, url, order_id):
        order_id = '%s_%s' % (order_id, data['act'])
        data['uid'] = tid
        data['orderid'] = order_id
        data['type'] = 'baijin'
        sign = xunleivip_generate_sign(data, settings.XUNLEIVIP_KEY)
        params = dict({'sign': sign}, **data)

        # 创建渠道订单记录
        channel_recode = get_user_channel_record(user.id)
        order = UserThreeOrder.objects.get_or_create(user=user, order_on=channel_recode, request_no=order_id)[0]
        order.save()

        # 异步回调
        xunleivip_callback.apply_async(
            kwargs={'url': url, 'params': params,
                    'channel': channel_recode.code, 'order_id': order_id})

    def recharge_call_back(self, obj, order_prefix=''):
        penny = Decimal(0.01).quantize(Decimal('.01'))
        pay_info = PayInfo.objects.filter(user=obj.user, type='D', amount__gt=penny,
                                          status=PayInfo.SUCCESS).order_by('create_time').first()

        # 判断用户是否绑定和首次充值
        if pay_info and int(pay_info.amount) >= 100:
            data = {
                'sendtype': '1',
                'num1': 7,
                'act': 5171
            }

            order_prefix = order_prefix or pay_info.order_id
            self.xunlei_call_back(obj.user, obj.bid, data,
                                  settings.XUNLEIVIP_CALL_BACK_URL,
                                  order_prefix)

    def purchase_call_back(self, obj, order_prefix=''):
        p2p_record = P2PRecord.objects.filter(user=obj.user, catalog=u'申购').order_by('create_time').first()

        # 判断是否首次投资
        if p2p_record and int(p2p_record.amount) >= 1000:
            data = {
                'sendtype': '0',
                'num1': 12,
                'act': 5170
            }

            order_prefix = order_prefix or p2p_record.order_id
            self.xunlei_call_back(obj.user, obj.bid, data,
                                  settings.XUNLEIVIP_CALL_BACK_URL,
                                  order_prefix)

    def save_model(self, request, obj, form, change):
        if obj.detect_callback is True and obj.btype == 'xunlei9':
            obj.detect_callback = False
            order_list = UserThreeOrder.objects.filter(user=obj.user, order_on__code=obj.btype)
            if order_list.exists():
                if order_list.count() == 1:
                    order_prefix, order_suffix = order_list.first().request_no.split('_')
                    if order_list.first().result_code:
                        if int(order_suffix) == 5170:
                            self.recharge_call_back(obj)
                        elif int(order_suffix) == 5171:
                            self.purchase_call_back(obj)
                    else:
                        if int(order_suffix) == 5170:
                            self.recharge_call_back(obj)
                            self.purchase_call_back(obj, order_prefix)
                        elif int(order_suffix) == 5171:
                            self.recharge_call_back(obj, order_prefix)
                            self.purchase_call_back(obj)
                else:
                    for order in order_list:
                        if order.result_code == '':
                            order_prefix, order_suffix = order.request_no.split('_')
                            if int(order_suffix) == 5170:
                                self.purchase_call_back(obj, order_prefix)
                            elif int(order_suffix) == 5171:
                                self.recharge_call_back(obj, order_prefix)
            else:
                self.recharge_call_back(obj)
                self.purchase_call_back(obj)

        obj.save()

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


class UserThreeOrderAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("user", "order_on", "request_no", "result_code", "created_at")
    search_fields = ('user__wanglibaouserprofile__phone', "request_no")
    raw_id_fields = ('user', )

    def has_delete_permission(self, request, obj=None):
        return False

class UserSourceAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'website', 'created_at']
    readonly_fields = ['keyword', 'website', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return  False

admin.site.register(UserSource, UserSourceAdmin)

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
admin.site.register(IdVerification, IdVerificationAdmin)
admin.site.register(VerifyCounter, VerifyCounterAdmin)
admin.site.register_view('accounts/id_verify/', view=AdminIdVerificationView.as_view(), name=u'网利宝-身份验证')
#admin.site.register_view('accounts/add_introduce/', view=IntroduceRelation.as_view(), name=u'网利宝-新增邀请')
admin.site.register(Binding, BindingAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(MessageText, MessageTextAdmin)
admin.site.register(UserPushId, UserPushIdAdmin)
admin.site.register(UserAddress, UserAddressAdmin)
admin.site.register(UserThreeOrder, UserThreeOrderAdmin, name=u'渠道订单记录')

admin.site.register_view('accounts/message/', view=AdminSendMessageView.as_view(), name=u'网利宝-发送站内信')
