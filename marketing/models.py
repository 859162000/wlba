# coding=utf-8

from django.db import models
from django.core.exceptions import ValidationError

from django import forms
from django.db import models
from django.utils.text import capfirst
from django.core import exceptions


class MultiSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple

    def __init__(self, *args, **kwargs):
        print ">>>>>>>>>>>>>a5"
        self.max_choices = kwargs.pop('max_choices', 0)
        super(MultiSelectFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        print ">>>>>>>>>>>>>a6"
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
        # if value and self.max_choices and len(value) > self.max_choices:
        #     raise forms.ValidationError('You must select a maximum of %s choice%s.'
        #             % (apnumber(self.max_choices), pluralize(self.max_choices)))
        return value


class MultiSelectField(models.Field):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        print ">>>>>>>>>>>>>aaa"
        return "CharField"

    def get_choices_default(self):
        print ">>>>>>>>>>>>bbb"
        return self.get_choices(include_blank=False)

    def _get_FIELD_display(self, field):
        print ">>>>>>>>>>>>>ccc"
        value = getattr(self, field.attname)
        choicedict = dict(field.choices)

    def formfield(self, **kwargs):
        print ">>>>>>>>>>>>>ddd"
        # don't call super, as that overrides default widget if it has choices
        defaults = {'required': not self.blank, 'label': capfirst(self.verbose_name),
                    'help_text': self.help_text, 'choices': self.choices}
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)

    def get_prep_value(self, value):
        print ">>>>>>>>>>>>>eee"
        return value

    def get_db_prep_value(self, value, connection=None, prepared=False):
        print ">>>>>>>>>>>>>fff"
        if isinstance(value, basestring):
            return value
        elif isinstance(value, list):
            return ",".join(value)

    def to_python(self, value):
        print ">>>>>>>>>>>>>ggg"
        if value is not None:
            return value if isinstance(value, list) else value.split(',')
        return ''

    def contribute_to_class(self, cls, name):
        print ">>>>>>>>>>>>>a1"
        super(MultiSelectField, self).contribute_to_class(cls, name)
        if self.choices:
            func = lambda self, fieldname = name, choicedict = dict(self.choices): ",".join([choicedict.get(value, value) for value in getattr(self, fieldname)])
            setattr(cls, 'get_%s_display' % self.name, func)

    def validate(self, value, model_instance):
        print ">>>>>>>>>>>>>a2"
        arr_choices = self.get_choices_selected(self.get_choices_default())
        for opt_select in value:
            print ">>>>>>>>>>>>>aaa", opt_select
            if (int(opt_select) not in arr_choices):  # the int() here is for comparing with integer choices
                raise exceptions.ValidationError(self.error_messages['invalid_choice'] % value)
        return

    def get_choices_selected(self, arr_choices=''):
        print ">>>>>>>>>>>>>a3"
        if not arr_choices:
            return False
        list = []
        for choice_selected in arr_choices:
            list.append(choice_selected[0])
        return list

    def value_to_string(self, obj):
        print ">>>>>>>>>>>>>a4"
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


class Channels(models.Model):
    """
        渠道信息
    """
    _FROM = (
        ('full', u'全平台'),
        ('pc', u'电脑端'),
        ('mobile', u'移动端'),
        ('ios', u'苹果'),
        ('android', u'安卓'),
        ('ios+pc', u'苹果和电脑端'),
        ('android+pc', u'安卓和电脑端')
    )

    _CLASS = (
        ('----', '----'),
        ('CPC', u'CPC-按点击计费'),
        ('CPD', u'CPD-按天计费'),
        ('CPT', u'CPT-按时间计费'),
        ('CPA', u'CPA-按行为计费'),
        ('CPS', u'CPS-按销售计费')
    )

    _STATUS = (
        (0, u'0-正常'),
        (1, u'1-暂停拉新'),
        (2, u'2-暂停合作'),
        (3, u'3-渠道归并')
    )

    _CALLBACK = (
        (u'注册', u'注册'),
        (u'实名', u'实名'),
        # ('binding', u'绑卡'),
        # ('first_investment', u'首投'),
        # ('investment', u'投资'),
        # ('first_pay', u'首充'),
        # ('pay', u'充值')
    )

    code = models.CharField(u'渠道代码', max_length=12, db_index=True, unique=True)
    name = models.CharField(u'渠道名字', max_length=20, default="")
    description = models.CharField(u'渠道描述', max_length=50, default="", blank=True)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
    image = models.ImageField(upload_to='channel', blank=True, default='',
                              verbose_name=u'渠道图片', help_text=u'主要用于渠道落地页的banner图片')
    coop_status = models.IntegerField(u'合作状态', max_length=2, default=0, choices=_STATUS)
    merge_code = models.CharField(u'并入渠道代码', blank=True, null=True, max_length=12)
    classification = models.CharField(u'渠道结算分类', max_length=20, default="----", choices=_CLASS)
    platform = models.CharField(u'渠道平台', max_length=20, default="full", choices=_FROM)
    start_at = models.DateTimeField(u'合作开始时间', blank=True, null=True, help_text=u'*可为空')
    end_at = models.DateTimeField(u'合作结束时间', blank=True, null=True, help_text=u'*可为空')
    is_abandoned = models.BooleanField(u'是否废弃', default=False)
    coop_callback = models.CharField(u'渠道回调', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = u"渠道"
        verbose_name = u"渠道"

    def clean(self):
        if len(self.code) == 6:
            raise ValidationError(u'为避免和邀请码重复，渠道代码长度不能等于6位')

        if self.coop_status == 3:
            if self.merge_code:
                ch = Channels.objects.filter(code=self.merge_code).first()
                if (not ch or ch.coop_status!=0 or ch.is_abandoned):
                    raise ValidationError(u'请输入正常状态的并入渠道代码')
                if (ch.code==self.code):
                    raise ValidationError(u'不能指定并入渠道为自己')
            else:
                raise ValidationError(u'设置状态为“渠道归并”时，请输入并入渠道代码')

    def __unicode__(self):
        return self.name
