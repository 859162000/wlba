# coding=utf-8

import requests
import logging
from django.conf import settings
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

logger = logging.getLogger(__name__)


def parse_id_verify_response_v2(text):
    import HTMLParser
    import lxml.html.soupparser as soupparser
    from .utils import base64_to_image

    html_parser = HTMLParser.HTMLParser()
    text = html_parser.unescape(text)

    root = soupparser.fromstring(text.encode('utf-8'))
    result_xm = next(root.iter('result_xm')).text
    result_gmsfhm = next(root.iter('result_gmsfhm')).text

    try:
        _root = soupparser.fromstring(text)
        _result_xm = next(_root.iter('result_xm')).text.encode('utf-8')
        _result_gmsfhm = next(_root.iter('result_gmsfhm')).text.encode('utf-8')

        if not(_result_xm == u'一致' == _result_gmsfhm):
            if _result_xm == '一致' == _result_gmsfhm:
                logger.exception('=20151211= text==>[%s], result_xm==>[%s, %s], result_gmsfhm==>[%s, %s] '
                                 'validate parse faild.' % (text, _result_xm, type(_result_xm),
                                                            _result_gmsfhm, type(_result_gmsfhm)))
    except Exception, e:
        logger.error('validate faild with error： %s ' % e)

    try:
        # xp's value type is base64
        xp = next(root.iter('xp')).text
        id_photo = base64_to_image(xp)
    except Exception:
        id_photo = None

    return {
        'result_xm': result_xm,
        'result_gmsfhm': result_gmsfhm,
        'id_photo': id_photo,
    }


class MyHttpsAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


def get_verify_result(id_number, name):
    import cgi

    inConditions = u"""<?xml version="1.0" encoding="UTF-8" ?>
        <ROWS>
            <INFO>
                <SBM>北京网利科技有限公司</SBM>
            </INFO>
            <ROW>
                <GMSFHM>公民身份号码</GMSFHM>
                <XM>姓名</XM>
            </ROW>
            <ROW FSD="100000" YWLX="个人理财">
                <GMSFHM>%s</GMSFHM>
                <XM>%s</XM>
            </ROW>
        </ROWS>"""

    inConditions = cgi.escape(inConditions % (id_number, name))

    request = u"""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                    <soap:Body>
                        <ns1:nciicCheck xmlns:ns1="http://serv.nciic.com">
                            <ns1:in0>%s</ns1:in0>
                            <ns1:in1>%s</ns1:in1>
                        </ns1:nciicCheck>
                    </soap:Body>
                    </soap:Envelope>""" % (settings.ID_LICENSE, inConditions)

    encode_request = request.encode('UTF-8')

    headers = {
        "Host": "api.nciic.com.cn",
        "SOAPAction": "",
        "Content-Type": "text/xml; charset=UTF-8",
        "Content-Length": len(encode_request),
    }

    s = requests.Session()
    s.mount('https://', MyHttpsAdapter(max_retries=5))
    response = s.post(url='https://api.nciic.com.cn/nciic_ws/services/NciicServices',
                      headers=headers,
                      data=encode_request,
                      verify=False)

    if response.status_code != 200:
        logger.error("validate failed to send request: status: %d, ", response.status_code)
        return None, "validate failed to send request"

    verify_result = False
    id_photo = None
    try:
        parsed_response = parse_id_verify_response_v2(response.text)
        result_xm = parsed_response['result_xm']
        result_gmsfhm = parsed_response['result_gmsfhm']
        if result_xm == u'一致' == result_gmsfhm:
            verify_result = True
            id_photo = parsed_response['id_photo']
        else:
            logger.error("id_number==>[%s], result_xm==>[%s, %s], result_gmsfhm==>[%s, %s]"
                         " validate faild" % (id_number, result_xm, type(result_xm),
                                              result_gmsfhm, type(result_gmsfhm)))
    except Exception, e:
        logger.error("reponse_text==>[%s]validate failed" % response.text)
        logger.error(e)

    return verify_result, id_photo
