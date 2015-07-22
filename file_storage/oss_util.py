import base64
import hmac
import mimetypes
import os
import re
import urllib
import urllib2
from wanglibao.settings import OSS_BUCKET, OSS_ENDPOINT, ACCESS_KEY, ACCESS_KEY_ID

from hashlib import md5, sha1
import time

DEFAULT_TIMEOUT = 10

def get_host():
    return '%s.%s'%(OSS_BUCKET, OSS_ENDPOINT)

def get_site_url(path):
    url =  'http://' + os.path.join(get_host(),  path)
    return url

def get_date():
    return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())

def get_authorization(action, path, content_md5, content_type, date):
    canonical_resource = os.path.join('/', OSS_BUCKET,  path)
    str_to_sign = '\n'.join([action, content_md5, content_type, date, canonical_resource])
    h = hmac.new(ACCESS_KEY,str_to_sign,sha1)
    signature = base64.encodestring(h.digest()).strip()
    authorization = 'OSS ' + ACCESS_KEY_ID + ':' + signature
    return authorization

def oss_save(path, file):
    """
    :param path: 使用相对路径
    :param file: 文件对象
    :return:
    """
    path = path.encode('utf-8')
    data=file.read()
    size = len(data)
    m = md5()
    m.update(data)
    content_md5 = base64.encodestring(m.digest()).strip()
    content_type = mimetypes.guess_type(path)[0] or ''
    date = get_date()

    opener = urllib2.build_opener(urllib2.HTTPHandler())
    request = urllib2.Request(get_site_url(path), data=data)
    request.add_header('Content-Length', size)
    request.add_header("Content-Type", content_type)
    request.add_header('Content-Md5', content_md5)
    request.add_header('Host', get_host())
    request.add_header('Date', date)
    action = 'PUT'
    request.add_header('Authorization', get_authorization(action, path,content_md5,content_type, date))
    request.get_method = lambda: action
    url = opener.open(request, timeout = DEFAULT_TIMEOUT)
    return size

def oss_delete(path):
    opener = urllib2.build_opener(urllib2.HTTPHandler())
    date = get_date()
    request = urllib2.Request(get_site_url(path))
    request.add_header('Host', get_host())
    request.add_header('Date', date)
    action = 'DELETE'
    request.add_header('Authorization', get_authorization(action, path, '','', date))
    request.get_method = lambda: action
    url = opener.open(request, timeout = DEFAULT_TIMEOUT)

def oss_open(path):
    opener = urllib2.build_opener(urllib2.HTTPHandler())
    date = get_date()
    request = urllib2.Request(get_site_url(path))
    request.add_header('Host', get_host())
    request.add_header('Date', date)
    action = 'GET'
    request.add_header('Authorization', get_authorization(action, path, '','', date))
    request.get_method = lambda: action
    return opener.open(request, timeout = DEFAULT_TIMEOUT)

if __name__ == '__main__':
    with open("/tmp/d.jpg") as f:
        oss_save('banner/200898163242920_2.jpg', f)
    print 'length %s' % len(oss_open('banner/200898163242920_2.jpg').read())
    # oss_delete('/tests.py')
