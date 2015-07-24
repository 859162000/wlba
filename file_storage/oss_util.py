# encoding:utf-8

import base64
import hmac
import mimetypes
import os
import re
import urllib
import StringIO
import httplib2
from wanglibao.settings import OSS_BUCKET, OSS_ENDPOINT, ACCESS_KEY, ACCESS_KEY_ID

from hashlib import md5, sha1
import time

DEFAULT_TIMEOUT = 10

def get_host():
    return '%s.%s'%(OSS_BUCKET, OSS_ENDPOINT)

def get_site_url(path):
    url =  'http://' + os.path.join(get_host(),  path)
    return url.encode('utf8')

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

    headers = {
        'Content-Length': size,
        "Content-Type": content_type,
        'Content-Md5': content_md5,
        'Host': get_host(),
        'Date': date,
        'Authorization': get_authorization('PUT', path, content_md5, content_type, date)
    }
    http = httplib2.Http()
    response, cont = http.request(get_site_url(path), 'PUT', headers=headers, body=data)
    if str(response['status']) == "200":
        return size
    else:
        raise IOError('IOError while save %s to OSS  with error message: %s and headers: %s'%(path, r.content, headers))

def oss_delete(path):
    date = get_date()
    headers = {
        'Host': get_host(),
        'Date': date,
        'Authorization': get_authorization('DELETE', path, '', '', date)
    }
    http = httplib2.Http()
    response, cont = http.request(get_site_url(path), 'DELETE', headers=headers)
    #200：成功，204：object不存在，404：bucket不存在
    return response['status']

def oss_open(path):
    date = get_date()
    headers = {
        'Host': get_host(),
        'Date': date,
        'Authorization': get_authorization('GET', path, '', '', date)
    }
    http = httplib2.Http()
    response, cont = http.request(get_site_url(path), 'GET', headers=headers)
    if str(response['status']) != "200":
        raise IOError('IOError while open %s from OSS  with error message: %s and headers: %s'%(path, r.content, headers))

    return StringIO.StringIO(cont)

if __name__ == '__main__':
    with open("/tmp/d.jpg") as f:
        oss_save('banner/200898163242920_2.jpg', f)
    print 'length %s' % len(oss_open('banner/200898163242920_2.jpg').read())
    oss_delete('banner/200898163242920_2.jpg')
    print 'length %s' % len(oss_open('banner/200898163242920_2.jpg').read())
