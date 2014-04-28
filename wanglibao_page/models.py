# -*- coding: utf-8 -*-
from django.db import models

from ckeditor.fields import RichTextField
# Create your models here.


class Catalog(models.Model):
    catalog = models.CharField(max_length=50, verbose_name='栏目名称')
    #catlog list order
    order = models.IntegerField(default=1000, verbose_name='显示顺序', help_text='数值越小，显示位置越靠前')
    created = models.DateField(verbose_name='创建时间', auto_now_add=True)

    def __unicode__(self):
        return '<Catalog %s>' % self.catalog

class Page(models.Model):
    title = models.CharField(max_length=100, verbose_name='标题', help_text='显示在浏览器标题栏和文章标题处')
    content = RichTextField()
    keywords = models.CharField(max_length=100, default='', help_text='html meta keywords')
    description = models.CharField(max_length=1000, default='', help_text='html meta description')

    catalog = models.ForeignKey(Catalog, related_name='pages', verbose_name='所属栏目')
    published = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True)
    update_data = models.DateField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return '<Page of %s, update: %s>' % (self.catalog.catalog, self.update_data)