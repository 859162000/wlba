# encoding:utf-8

import json
from django import forms
from django.contrib import admin
from marketing.models import Channels


class ChannelForm(forms.ModelForm):
    coop_callback = forms.MultipleChoiceField(label=u'渠道回调', choices=Channels._CALLBACK,
                                              widget=forms.CheckboxSelectMultiple(), required=False)

    class Meta:
        model = Channels


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

admin.site.register(Channels, ChannelsAdmin)
