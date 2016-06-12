# encoding:utf-8

import json
from django import forms
from django.contrib import admin
from django.db.models import Q
from marketing.models import Channels, ChannelParams


class ChannelForm(forms.ModelForm):
    coop_callback = forms.MultipleChoiceField(label=u'渠道回调', choices=Channels._CALLBACK,
                                              widget=forms.CheckboxSelectMultiple(), required=False)

    def clean_code(self):
        code = self.cleaned_data['code']
        if len(code) == 6:
            raise forms.ValidationError(u'为避免和邀请码重复，渠道代码长度不能等于6位')

        return code

    def clean_merge_code(self):
        code = self.cleaned_data['code']
        coop_status = self.cleaned_data['coop_status']
        merge_code = self.cleaned_data['merge_code']
        is_abandoned = self.cleaned_data['is_abandoned']
        if coop_status == 3 and not is_abandoned:
            if merge_code:
                if merge_code == code:
                    raise forms.ValidationError(u'不能指定并入渠道为自己')
                else:
                    channel = Channels.objects.filter(code=merge_code).first()
                    if not channel or channel.coop_status != 0 or channel.is_abandoned:
                        raise forms.ValidationError(u'请输入正常状态的并入渠道码')
            else:
                raise forms.ValidationError(u'设置状态为“渠道归并”时，请输入并入渠道码')

        return merge_code

    class Meta:
        model = Channels


class ChannelParamsForm(forms.ModelForm):
    get_from = forms.MultipleChoiceField(label=u'参数获取', choices=ChannelParams.PARAMS_SOURCES,
                                         widget=forms.CheckboxSelectMultiple())

    def clean_parent(self):
        name = self.cleaned_data['name']
        params_parent = self.cleaned_data['parent']
        params_level = self.cleaned_data['level']
        if params_level == 2:
            if not params_parent:
                raise forms.ValidationError(u'子级参数必须指定父级参数名')
            else:
                if params_parent == name:
                    raise forms.ValidationError(u'不能指定父级参数名为自己')
                else:
                    channel = self.cleaned_data['channel']
                    channel_params = ChannelParams.objects.filter(channel=channel, name=params_parent)
                    if not channel_params.exists():
                        raise forms.ValidationError(u'无效父级参数名')

        return params_parent

    class Meta:
        model = ChannelParams


class ChannelsAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("id", "code", "name", "description", "platform", "coop_status", "is_abandoned")
    search_fields = ("name",)
    list_filter = ("coop_status", "is_abandoned", "classification")
    form = ChannelForm

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.coop_callback = json.dumps(obj.coop_callback)
        obj.save()


class ChannelParamsAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("name", "external_name", "description", "default_value", "is_abandoned", "created_at")
    search_fields = ("name",)
    list_filter = ("is_abandoned",)
    raw_id_fields = ('channel',)
    form = ChannelParamsForm

    def save_model(self, request, obj, form, change):
        obj.get_from = json.dumps(obj.get_from)
        decrypt_method = obj.decrypt_method
        if decrypt_method == 'None':
            obj.decrypt_method = None
        obj.save()


admin.site.register(Channels, ChannelsAdmin)
admin.site.register(ChannelParams, ChannelParamsAdmin)
