# coding=utf-8
from django.db import models


class File(models.Model):
    path = models.CharField(u'文件路径', max_length=128, db_index=True, unique=True)
    content = models.BinaryField(u'内容(20M max)', max_length=20 * 1024 * 1024)
    size = models.PositiveIntegerField(u'大小', default=0)
    updated_at = models.DateTimeField(u'修改时间', auto_now=True)

    def __unicode__(self):
        return self.path
