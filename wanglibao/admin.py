from django.core.exceptions import PermissionDenied
from django.contrib import admin
 
 
class ReadPermissionModelAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        if getattr(request, 'readonly', False):
            return True
        return super(ReadPermissionModelAdmin, self).has_change_permission(request, obj)
 
    def changelist_view(self, request, extra_context=None):
        try:
            return super(ReadPermissionModelAdmin, self).changelist_view(
                request, extra_context=extra_context)
        except PermissionDenied:
            pass
        if request.method == 'POST':
            raise PermissionDenied
        request.readonly = True
        return super(ReadPermissionModelAdmin, self).changelist_view(
            request, extra_context=extra_context)
 
    def change_view(self, request, object_id, extra_context=None):
        try:
            return super(ReadPermissionModelAdmin, self).change_view(
                request, object_id, extra_context=extra_context)
        except PermissionDenied:
            pass
        if request.method == 'POST':
            raise PermissionDenied
        request.readonly = True
        return super(ReadPermissionModelAdmin, self).change_view(
            request, object_id, extra_context=extra_context)


from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import escape
from django.core.urlresolvers import reverse


class LogEntryAdmin(admin.ModelAdmin):

    # date_hierarchy = 'action_time'

    readonly_fields = LogEntry._meta.get_all_field_names()

    search_fields = [
        'user__wanglibaouserprofile__phone'
    ]


    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag',
        'change_message',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = u'<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return link
    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = u'object'

    def queryset(self, request):
        return super(LogEntryAdmin, self).queryset(request) \
            .prefetch_related('content_type')


admin.site.register(LogEntry, LogEntryAdmin)