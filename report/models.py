# coding=utf-8
from django.core.files.storage import FileSystemStorage
from django.db import models


class MyFileStorage(FileSystemStorage):

    # This method is actually defined in Storage
    def get_available_name(self, name):
      return name # simply returns the name passed

mfs = MyFileStorage()


class Report(models.Model):
    name = models.CharField(u'表格名称', max_length=128, blank=True)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
    file = models.FileField(u'文件', null=True, upload_to='reports', storage=mfs)

    class Meta:
        verbose_name_plural = u'导出表格'
