# encoding: utf-8

import re
import ssl
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from django.utils import timezone


try:
    unicode
except NameError:
    def _is_unicode(x):
        return 0
else:
    def _is_unicode(x):
        return isinstance(x, unicode)

_hexdig = '0123456789ABCDEFabcdef'
_hextochr = dict((a + b, chr(int(a + b, 16)))
                 for a in _hexdig for b in _hexdig)
_asciire = re.compile('([\x00-\x7f]+)')


always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')
_safe_map = {}
for i, c in zip(xrange(256), str(bytearray(xrange(256)))):
    _safe_map[c] = c if (i < 128 and c in always_safe) else '%{:02X}'.format(i)
_safe_quoters = {}


class StrQuote(object):

    def unquote(self, s):
        """unquote('abc%20def') -> 'abc def'."""
        if _is_unicode(s):
            if '%' not in s:
                return s
            bits = _asciire.split(s)
            res = [bits[0]]
            append = res.append
            for i in range(1, len(bits), 2):
                append(self.unquote(str(bits[i])).decode('latin1'))
                append(bits[i + 1])
            return ''.join(res)

        bits = s.split('%')
        # fastpath
        if len(bits) == 1:
            return s
        res = [bits[0]]
        append = res.append
        for item in bits[1:]:
            try:
                append(_hextochr[item[:2]])
                append(item[2:])
            except KeyError:
                append('%')
                append(item)
        return ''.join(res)

    def unquote_plus(self, s):
        """unquote('%7e/abc+def') -> '~/abc def'"""
        s = s.replace('+', ' ')
        return self.unquote(s)

    def quote(self, s, safe='/'):
        """quote('abc def') -> 'abc%20def'

        Each part of a URL, e.g. the path info, the query, etc., has a
        different set of reserved characters that must be quoted.

        RFC 2396 Uniform Resource Identifiers (URI): Generic Syntax lists
        the following reserved characters.

        reserved    = ";" | "/" | "?" | ":" | "@" | "&" | "=" | "+" |
                      "$" | ","

        Each of these characters is reserved in some component of a URL,
        but not necessarily in all of them.

        By default, the quote function is intended for quoting the path
        section of a URL.  Thus, it will not encode '/'.  This character
        is reserved, but in typical usage the quote function is being
        called on a path where the existing slash characters are used as
        reserved characters.
        """
        # fastpath
        if not s:
            if s is None:
                raise TypeError('None object cannot be quoted')
            return s
        cachekey = (safe, always_safe)
        try:
            (quoter, safe) = _safe_quoters[cachekey]
        except KeyError:
            safe_map = _safe_map.copy()
            safe_map.update([(c, c) for c in safe])
            quoter = safe_map.__getitem__
            safe = always_safe + safe
            _safe_quoters[cachekey] = (quoter, safe)
        if not s.rstrip(safe):
            return s
        return ''.join(map(quoter, s))

    def quote_plus(self, s, safe=''):
        """Quote the query fragment of a URL; replacing ' ' with '+'"""
        if ' ' in s:
            s = self.quote(s, safe + ' ')
            return s.replace(' ', '+')
        return self.quote(s, safe)


class FileObject(object):
    """构造文件对象（file, size云存储所需）"""

    def __init__(self, content, size):
        self.file = content
        self.size = size


class MyHttpsAdapter(HTTPAdapter):
    """指定https请求时使用TLSv1版本"""

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


def atr_to_atr_for_obj(atr_map, obj):
    for src_atr_key, dst_atr_key in atr_map:
        src_atr = getattr(obj, src_atr_key)
        setattr(obj, dst_atr_key, src_atr)

    return obj


def utc_to_local_timestamp(time_obj=timezone.now()):
    time_format = '%Y-%m-%d %H:%M:%S'
    utc_time = timezone.localtime(time_obj).strftime(time_format)
    utc_timestamp = str(int(time.mktime(time.strptime(utc_time, time_format))))
    return utc_timestamp


def chunks(l, n):
    """把一个list分成多个长度最长为n的小list"""
    for i in range(0, len(l), n):
        yield l[i:i+n]

def update_by_keys(dict1, dict2, *key_args):
    """
    >>> d1 = {}
    >>> d2 = {'k1':1,'k2':2,'k3':3}
    >>> d1={}
    >>> update_by_keys(d1, d2, 'k1', 'k2')
    >>> d1
    {'k2': 2, 'k1': 1}
    """
    dict1.update([(k,v) for k,v in dict2.items() if k in key_args])









