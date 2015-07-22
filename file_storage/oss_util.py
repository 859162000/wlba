import base64
import hmac
import os
import re
import sha
import urllib
import urllib2
from wanglibao.settings import OSS_BUCKET, OSS_ENDPOINT, ACCESS_KEY, ACCESS_KEY_ID

__author__ = 'guoya'
from hashlib import md5
import time

DEFAULT_TIMEOUT = 10

def get_host():
    return '%s.%s'%(OSS_BUCKET, OSS_ENDPOINT)

def get_site_url(path):
    url =  'http://' + os.path.join(get_host(),  path)
    return url

def get_content_type(path):
     type_list = {
                'html'  :       'text/html',
                'htm'   :       'text/html',
                'shtml' :       'text/html',
                'css'   :       'text/css',
                'xml'   :       'text/xml',
                'gif'   :       'image/gif',
                'jpeg'  :       'image/jpeg',
                'jpg'   :       'image/jpeg',
                'js'    :       'application/x-javascript',
                'atom'  :       'application/atom+xml',
                'rss'   :       'application/rss+xml',
                'mml'   :       'text/mathml',
                'txt'   :       'text/plain',
                'jad'   :       'text/vnd.sun.j2me.app-descriptor',
                'wml'   :       'text/vnd.wap.wml',
                'htc'   :       'text/x-component',
                'png'   :       'image/png',
                'tif'   :       'image/tiff',
                'tiff'  :       'image/tiff',
                'wbmp'  :       'image/vnd.wap.wbmp',
                'ico'   :       'image/x-icon',
                'jng'   :       'image/x-jng',
                'bmp'   :       'image/x-ms-bmp',
                'svg'   :       'image/svg+xml',
                'svgz'  :       'image/svg+xml',
                'webp'  :       'image/webp',
                'jar'   :       'application/java-archive',
                'war'   :       'application/java-archive',
                'ear'   :       'application/java-archive',
                'hqx'   :       'application/mac-binhex40',
                'doc'   :       'application/msword',
                'pdf'   :       'application/pdf',
                'ps'    :       'application/postscript',
                'eps'   :       'application/postscript',
                'ai'    :       'application/postscript',
                'rtf'   :       'application/rtf',
                'xls'   :       'application/vnd.ms-excel',
                'ppt'   :       'application/vnd.ms-powerpoint',
                'wmlc'  :       'application/vnd.wap.wmlc',
                'kml'   :       'application/vnd.google-earth.kml+xml',
                'kmz'   :       'application/vnd.google-earth.kmz',
                '7z'    :       'application/x-7z-compressed',
                'cco'   :       'application/x-cocoa',
                'jardiff'       :       'application/x-java-archive-diff',
                'jnlp'  :       'application/x-java-jnlp-file',
                'run'   :       'application/x-makeself',
                'pl'    :       'application/x-perl',
                'pm'    :       'application/x-perl',
                'prc'   :       'application/x-pilot',
                'pdb'   :       'application/x-pilot',
                'rar'   :       'application/x-rar-compressed',
                'rpm'   :       'application/x-redhat-package-manager',
                'sea'   :       'application/x-sea',
                'swf'   :       'application/x-shockwave-flash',
                'sit'   :       'application/x-stuffit',
                'tcl'   :       'application/x-tcl',
                'tk'    :       'application/x-tcl',
                'der'   :       'application/x-x509-ca-cert',
                'pem'   :       'application/x-x509-ca-cert',
                'crt'   :       'application/x-x509-ca-cert',
                'xpi'   :       'application/x-xpinstall',
                'xhtml' :       'application/xhtml+xml',
                'zip'   :       'application/zip',
                'bin'   :       'application/octet-stream',
                'exe'   :       'application/octet-stream',
                'dll'   :       'application/octet-stream',
                'deb'   :       'application/octet-stream',
                'dmg'   :       'application/octet-stream',
                'eot'   :       'application/octet-stream',
                'iso'   :       'application/octet-stream',
                'img'   :       'application/octet-stream',
                'msi'   :       'application/octet-stream',
                'msp'   :       'application/octet-stream',
                'msm'   :       'application/octet-stream',
                'mid'   :       'audio/midi',
                'midi'  :       'audio/midi',
                'kar'   :       'audio/midi',
                'mp3'   :       'audio/mpeg',
                'ogg'   :       'audio/ogg',
                'm4a'   :       'audio/x-m4a',
                'ra'    :       'audio/x-realaudio',
                '3gpp'  :       'video/3gpp',
                '3gp'   :       'video/3gpp',
                'mp4'   :       'video/mp4',
                'mpeg'  :       'video/mpeg',
                'mpg'   :       'video/mpeg',
                'mov'   :       'video/quicktime',
                'webm'  :       'video/webm',
                'flv'   :       'video/x-flv',
                'm4v'   :       'video/x-m4v',
                'mng'   :       'video/x-mng',
                'asx'   :       'video/x-ms-asf',
                'asf'   :       'video/x-ms-asf',
                'wmv'   :       'video/x-ms-wmv',
                'avi'   :       'video/x-msvideo'
                }
     try:
        ext = path.split('.')[-1]
        return type_list[ext]
     except:
        return ''

def get_date():
    return time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())

def get_authorization(action, path, content_md5, content_type, date):
    canonical_resource = os.path.join('/', OSS_BUCKET,  path)
    str_to_sign = '\n'.join([action, content_md5, content_type, date, canonical_resource])
    # print str_to_sign, len(str_to_sign)
    h = hmac.new(ACCESS_KEY,str_to_sign,sha)
    signature = base64.encodestring(h.digest()).strip()
    authorization = 'OSS ' + ACCESS_KEY_ID + ':' + signature
    return authorization

def oss_save(path, file):
    path = path.encode('utf-8')
    data=file.read()
    # print type(data), len(data)
    size = len(data)
    m = md5()
    m.update(data)
    content_md5 = base64.encodestring(m.digest()).strip()
    content_type = get_content_type(path)
    date = get_date()

    opener = urllib2.build_opener(urllib2.HTTPHandler())
    # print 'data'+ data
    # print '========'+get_site_url(path)
    request = urllib2.Request(get_site_url(path), data=data)
    request.add_header('Content-Length', size)
    request.add_header("Content-Type", content_type)
    request.add_header('Content-Md5', content_md5)
    request.add_header('Host', get_host())
    request.add_header('Date', date)
    action = 'PUT'
    request.add_header('Authorization', get_authorization(action, path,content_md5,content_type, date))
    request.get_method = lambda: action
    try:
        url = opener.open(request, timeout = DEFAULT_TIMEOUT)
        # print 'get size %s' % size
        return size
    except urllib2.HTTPError, e:
        c = e.fp.read()
        # print c
        raise e
        # m = re.findall(r'<StringToSign>(.*)</StringToSign>', c, re.S)[0]
        # h = hmac.new(ACCESS_KEY,m,sha)
        # signature = base64.encodestring(h.digest()).strip()
        # print signature
        # # ali_str = ''.join(([chr(int(i, 16)) for i in m.split(' ') if i != '']))
        # # print ali_str, len(ali_str)

def oss_delete(path):
    opener = urllib2.build_opener(urllib2.HTTPHandler())
    # print 'data'+ data
    date = get_date()
    request = urllib2.Request(get_site_url(path))
    request.add_header('Host', get_host())
    request.add_header('Date', date)
    action = 'DELETE'
    request.add_header('Authorization', get_authorization(action, path, '','', date))
    request.get_method = lambda: action
    try:
        url = opener.open(request, timeout = DEFAULT_TIMEOUT)
    except urllib2.HTTPError, e:
        c = e.fp.read()
        # print c
        raise e

def oss_open(path):
    opener = urllib2.build_opener(urllib2.HTTPHandler())
    # print 'data'+ data
    date = get_date()
    request = urllib2.Request(get_site_url(path))
    request.add_header('Host', get_host())
    request.add_header('Date', date)
    action = 'GET'
    request.add_header('Authorization', get_authorization(action, path, '','', date))
    request.get_method = lambda: action
    try:
        return opener.open(request, timeout = DEFAULT_TIMEOUT)
    except urllib2.HTTPError, e:
        c = e.fp.read()
        # print c

if __name__ == '__main__':
    with open("/tmp/d.jpg") as f:
        oss_save('banner/200898163242920_2.jpg', f)
    print 'length %s' % len(oss_open('banner/200898163242920_2.jpg').read())
    # oss_delete('/tests.py')
