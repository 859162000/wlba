# encoding:utf-8

import os
import random
from urlparse import urljoin
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.db import IntegrityError
from django.middleware.transaction import transaction
from file_storage.models import File
from file_storage.oss_util import oss_save, oss_open, oss_delete
from wanglibao.settings import MEDIA_URL


class DatabaseStorage(Storage):

    def __init__(self):
        super(DatabaseStorage, self).__init__()

        self.base_url = settings.MEDIA_URL

    def save(self, name, content):
        original_name, ext = os.path.splitext(name)
        filename = original_name

        count = 10
        content_data = content.file.read()
        while count:
            count -= 1
            try:
                with transaction.atomic():
                    file_record = File()
                    file_record.path = filename + ext
                    file_record.content = content_data
                    file_record.size = len(content)
                    file_record.save()
                    return file_record.path
            except IntegrityError, e:
                filename = u'%s_%d' % (original_name, random.randrange(0, 10000))
                continue

    def open(self, name, mode='rb'):
        file_record = File.objects.get(path=name)
        return ContentFile(file_record.content)

    def delete(self, name):
        File.objects.filter(path=name).delete()

    def exists(self, name):
        return File.objects.filter(path=name).exists()

    def listdir(self, path):
        raise NotImplementedError()

    def size(self, name):
        file_ = File.objects.get(path=name)
        return file_.size

    def url(self, name):
        return urljoin(self.base_url, name)


class AliOSSStorage(Storage):
    def __init__(self):
        super(AliOSSStorage, self).__init__()
        self.base_url = settings.MEDIA_URL

    def save(self, name, content):
        size = oss_save(name, content.file)
        #如果上传重名则覆盖
        f = File.objects.get_or_create(path=name)[0]
        f.size = size
        f.save()
        return name

    def open(self, name, mode='rb'):
        File.objects.get(path=name)
        return oss_open(name)

    def delete(self, name):
        oss_delete(name)
        File.objects.filter(path=name).delete()

    def exists(self, name):
        return File.objects.filter(path=name).exists()

    def listdir(self, path):
        raise NotImplementedError()

    def size(self, name):
        try:
            return File.objects.get(path=name).size
        except:
            return 0

    def modified_time(self, name):
        try:
            return File.objects.get(path=name).updated_at
        except:
            return None

    def url(self, name):
        return urljoin(self.base_url, name)




