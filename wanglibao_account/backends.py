# coding=utf-8

import re
import ssl
import logging
import datetime
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from django.conf import settings
from django.db.models import Sum
from wanglibao_account.models import IdVerification, UserSource
from wanglibao_redpack.models import Income, PhpIncome

logger = logging.getLogger("wanglibao_account")


def broker_invite_list(user):
    users = {}
    records = Income.objects.filter(user=user, paid=True).select_related('user__wanglibaouserprofile', 'invite__wanglibaouserprofile').all()
    php_records = PhpIncome.objects.filter(user=user, paid=True).select_related('user__wanglibaouserprofile', 'invite__wanglibaouserprofile').all()
    first_amount = first_earning = second_amount = second_earning = first_count = second_count = 0
    first_intro = []
    commission = {} 
    for rd in records:
        isNew = False
        if rd.user_id not in users:
            users[rd.user_id] = rd.user.wanglibaouserprofile
        if rd.invite_id not in users:
            isNew = True
            users[rd.invite_id] = rd.invite.wanglibaouserprofile
        if rd.invite_id not in commission:
            commission[rd.invite_id] = {"amount":0, "earning":0}
        if rd.level == 1:
            first_amount += rd.amount
            first_earning += rd.earning
            if isNew:
                first_count += 1
            commission[rd.invite_id]["amount"] += rd.amount
            commission[rd.invite_id]["earning"] += rd.earning
        else:
            second_amount += rd.amount
            second_earning += rd.earning
            if isNew:
                second_count += 1

    for rd in php_records:
        isNew = False
        if rd.user_id not in users:
            users[rd.user_id] = rd.user.wanglibaouserprofile
        if rd.invite_id not in users:
            isNew = True
            users[rd.invite_id] = rd.invite.wanglibaouserprofile
        if rd.invite_id not in commission:
            commission[rd.invite_id] = {"amount":0, "earning":0}
        if rd.level == 1:
            first_amount += rd.amount
            first_earning += rd.earning
            if isNew:
                first_count += 1
            commission[rd.invite_id]["amount"] += rd.amount
            commission[rd.invite_id]["earning"] += rd.earning
        else:
            second_amount += rd.amount
            second_earning += rd.earning
            if isNew:
                second_count += 1

    return {"first_amount":first_amount, "first_earning":first_earning,
            "second_amount":second_amount, "second_earning":second_earning,
            "first_count":first_count, "second_count":second_count,
            "first_intro":first_intro, "commission":commission,
            "users":users}


def invite_earning(user):
    amount = Income.objects.filter(user=user, paid=True).aggregate(Sum('earning'))
    if amount['earning__sum']:
        earning = amount['earning__sum']
    else:
        earning = 0
    return earning


def set_source(request, user):
    # Add try-except by hb on 2015-11-20
    try:
        keyword = request.session.get("promo_source_keyword", "")
        if keyword:
            source = UserSource.objects.create(
                user=user,
                action='register',
                keyword=keyword,
                site_name=request.session.get("promo_source_site_name", ""),
                website=request.session.get("promo_source_website", "")
            )
            logger.debug("注册行为已经完成，SEM统计参量入库,object value:{0}".format(source))
    except Exception, reason:
        logger.debug("SEM关键词统计，入库报异常；reason:%s" % reason)


class TestIDVerifyBackEnd(object):

    @classmethod
    def verify(cls, name, id_number):
        records = IdVerification.objects.filter(id_number=id_number, name=name)
        if records.exists():
            record = records.first()
            return record, None

        record = IdVerification(id_number=id_number, name=name, is_valid=True)
        record.save()

        return record, None


class ProductionIDVerifyBackEnd(object):

    @classmethod
    def verify(cls, name, id_number):
        records = IdVerification.objects.filter(id_number=id_number, name=name)
        if records.exists():
            record = records.first()
            return record, None

        request = u"""<?xml version="1.0" encoding="utf-8"?>
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:nci="http://www.nciic.com.cn" xmlns:fin="http://schemas.datacontract.org/2004/07/Finance.EPM">
               <soapenv:Header/>
               <soapenv:Body>
                  <nci:SimpleCheck>
                     <!--Optional:-->
                     <nci:request>
                        <!--Optional:-->
                        <fin:IDNumber>%s</fin:IDNumber>
                        <!--Optional:-->
                        <fin:Name>%s</fin:Name>
                     </nci:request>
                     <!--Optional:-->
                     <nci:cred>
                        <!--Optional:-->
                        <fin:BindInfo></fin:BindInfo>
                        <!--Optional:-->
                        <fin:Password>%s</fin:Password>
                        <!--Optional:-->
                        <fin:UserName>%s</fin:UserName>
                     </nci:cred>
                  </nci:SimpleCheck>
               </soapenv:Body>
            </soapenv:Envelope>"""

        encoded_request = (request % (id_number, name, settings.ID_VERIFY_PASSWORD, settings.ID_VERIFY_USERNAME)).encode("utf-8")

        headers = {
            "Host": "service.sfxxrz.com",
            "SOAPAction": "http://www.nciic.com.cn/IIdentifierService/SimpleCheck",
            "Content-Type": "text/xml; charset=UTF-8",
            "Content-Length": len(encoded_request),
        }

        response = requests.post(url='http://service.sfxxrz.com/IdentifierService.svc',
                                 headers=headers,
                                 data=encoded_request,
                                 verify=False)

        if response.status_code != 200:
            logger.error("Failed to send request: status: %d, ", response.status_code)
            return None, "Failed to send request"

        try:
            verify_result = False
            parsed_response = parse_id_verify_response(response.text)
            if parsed_response['result'] == u'一致':
                verify_result = True
        except StopIteration:
            pass

        # result = bool(parsed_response['response_code'] == 100)
        #
        # if not result:
        #     logger.error("Failed to validate: %s" % response.text)
        #
        # verify_result = True
        # if parsed_response['result'] != u'一致':
        #     verify_result = False
        #     logger.info("Identity not consistent %s" % response.text)

        record = IdVerification(id_number=id_number, name=name, is_valid=verify_result)
        record.save()

        return record, None


class ProductionIDVerifyV2BackEnd(object):
    """用户实名认证接口v2"""

    @classmethod
    def verify(cls, name, id_number):
        records = IdVerification.objects.filter(id_number=id_number, name=name)
        if records.exists():
            record = records.first()
            return record, None

        verify_result, id_photo, message = get_verify_result(id_number, name)

        record = IdVerification()
        record.id_number = id_number
        record.name = name
        record.is_valid = verify_result
        record.description = message

        if verify_result and id_photo:
            record.id_photo.save('%s.jpg' % id_number, id_photo, save=True)

        record.save()

        return record, None


def parse_id_verify_response_v2(text):
    """实名结果(xml)解析"""

    import HTMLParser
    import lxml.html.soupparser as soupparser
    from .utils import base64_to_image

    # html转义
    html_parser = HTMLParser.HTMLParser()
    text = html_parser.unescape(text)

    id_photo = None
    result_xm = None
    result_gmsfhm = None
    message = ""
    root = soupparser.fromstring(text.encode('utf-8'))
    # 解析身份证id和姓名认证结果
    try:
        result_xm = next(root.iter('result_xm')).text
        result_gmsfhm = next(root.iter('result_gmsfhm')).text
    except StopIteration, e:
        try:
            message = next(root.iter('errormesage')).text
        except StopIteration, e:
            message = next(root.iter('errormsg')).text

    # 解析相片
    if result_xm and result_gmsfhm:
        try:
            # xp's value type is base64
            xp = next(root.iter('xp')).text
            if xp:
                id_photo = base64_to_image(xp)
            else:
                message = u'库中无相片'
        except Exception:
            message = u'图片解析失败'

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

    return {
        'result_xm': result_xm,
        'result_gmsfhm': result_gmsfhm,
        'id_photo': id_photo,
        'message': message,
    }


class MyHttpsAdapter(HTTPAdapter):
    """指定https请求时使用TLSv1版本"""

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


def check_birth_date_for_id(id_number):
    """根据身份证判断出生日期是否合法"""

    id_number = str(id_number)
    if len(id_number) == 15:
        birth_date = '19' + id_number[6:12]
    else:
        birth_date = id_number[6:14]

    _month = birth_date[4:6]
    _day = birth_date[6:]
    if 0 < int(_month) <= 12 and 0 < int(_day) <= 31:
        return True
    return False


def check_age_for_id(id_number):
    """根据身份证计算年龄并判断"""

    id_number = str(id_number)
    if len(id_number) == 15:
        birth_date = '19' + id_number[6:12]
    else:
        birth_date = id_number[6:14]

    # 判断该身份证用户年龄是否大于或等于18周岁
    current_date = datetime.datetime.now()
    birth_date = datetime.datetime.strptime(birth_date, '%Y%m%d')

    # 如果出生日期小于当前日期则进入判断
    if birth_date < current_date:
        # 今年减去出生年得出周岁，如果今年的生日还没过周岁再减一
        age = current_date.year - birth_date.year
        if int(current_date.strftime('%Y%m%d')[4:]) < int(birth_date.strftime('%Y%m%d')[4:]):
            age -= 1

        if age >= 18:
            return True

    return False


def check_area_for_id(area_code):
    """判断身份证所在地"""

    area = {
        "11": u"北京", "12": u"天津", "13": u"河北", "14": u"山西", "15": u"内蒙古", "21": u"辽宁",
        "22": u"吉林", "23": u"黑龙江", "31": u"上海", "32": u"江苏", "33": u"浙江", "34": u"安徽",
        "35": u"福建", "36": u"江西", "37": u"山东", "41": u"河南", "42": u"湖北", "43": u"湖南",
        "44": u"广东", "45": u"广西", "46": u"海南", "50": u"重庆", "51": u"四川", "52": u"贵州",
        "53": u"云南", "54": u"西藏", "61": u"陕西", "62": u"甘肃", "63": u"青海", "64": u"宁夏",
        "65": u"新疆", "71": u"台湾", "81": u"香港", "82": u"澳门", "91": u"国外",
    }

    if area[str(area_code)]:
        return True

    return False


def check_id_card(id_number):
    """身份证合法性校验"""

    Errors = [u'验证通过!', u'身份证号码位数不对!', u'身份证号码出生日期不合法!',
              u'身份证号码校验错误!', u'身份证地区非法!', u'用户未满18周岁']

    _Wi = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]

    id_number = str(id_number).strip()

    # 地区校验
    if not check_area_for_id(id_number[0:2]):
        return False, Errors[4]

    # 15位身份号码检测
    if len(id_number) == 15:
        if (int(id_number[6:8]) + 1900) % 4 == 0 or ((int(id_number[6:8]) + 1900) % 100 == 0
                                                     and (int(id_number[6:8]) + 1900) % 4 == 0):
            # 测试出生日期的合法性
            ereg = re.compile('[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|'
                              '(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$')
        else:
            # 测试出生日期的合法性
            ereg = re.compile('[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|'
                              '(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$')

        if re.match(ereg, id_number):
            return True, Errors[0]
        else:
            return False, Errors[2]

    # 18位身份号码检测
    elif len(id_number) == 18:
        # 出生日期的合法性检查
        # 闰年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))
        # 平年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))
        if int(id_number[6:10]) % 4 == 0 or (int(id_number[6:10]) % 100 == 0 and int(id_number[6:10]) % 4 == 0):
            # 闰年出生日期的合法性正则表达式
            ereg = re.compile('[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|'
                              '(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9Xx]$')
        else:
            # 平年出生日期的合法性正则表达式
            ereg = re.compile('[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|'
                              '(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9Xx]$')

        # 测试出生日期的合法性
        if re.match(ereg, id_number):
            # 测试用户是否大于或等于18周岁
            if check_age_for_id(id_number):
                # 计算校验位
                _sum = sum([int(id_number[i]) * _Wi[i] for i in range(17)])
                Y = _sum % 11
                JYM = "10X98765432"
                M = JYM[Y]
                # 检测ID的校验位
                if M == id_number[17]:
                    return True, Errors[0]
                else:
                    return False, Errors[3]
            else:
                return False, Errors[5]
        else:
            return False, Errors[2]
    else:
        return False, Errors[1]


def get_verify_result(id_number, name):
    import cgi

    verify_result = False
    id_photo = None

    # 身份证合法性校验
    # check_result, _error = check_id_card(id_number)
    # if not check_result:
    #     return verify_result, id_photo, _error

    # 身份证出生日期合法性校验
    if not check_birth_date_for_id(id_number):
        return verify_result, id_photo, u'身份证出生日期不合法'

    # 根据身份证号出生日期判断用户是否大于或等于18周岁
    if not check_age_for_id(id_number):
        return verify_result, id_photo, u'该用户未满18周岁'

    in_conditions = u"""<?xml version="1.0" encoding="UTF-8" ?>
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

    # html转义
    in_conditions = cgi.escape(in_conditions % (id_number, name))

    request = u"""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                    <soap:Body>
                        <ns1:nciicCheck xmlns:ns1="http://serv.nciic.com">
                            <ns1:in0>%s</ns1:in0>
                            <ns1:in1>%s</ns1:in1>
                        </ns1:nciicCheck>
                    </soap:Body>
                    </soap:Envelope>""" % (settings.ID_LICENSE, in_conditions)

    encode_request = request.encode('UTF-8')

    headers = {
        "Host": "api.nciic.com.cn",
        "SOAPAction": "",
        "Content-Type": "text/xml; charset=UTF-8",
        "Content-Length": len(encode_request),
    }

    # 发送实名认证请求
    s = requests.Session()
    s.mount('https://', MyHttpsAdapter(max_retries=5))
    response = s.post(url='https://api.nciic.com.cn/nciic_ws/services/NciicServices',
                      headers=headers,
                      data=encode_request,
                      verify=False)

    if response.status_code != 200:
        logger.error("validate failed to send request: status: %d, ", response.status_code)
        return verify_result, id_photo, u"连接错误：%s" % response.status_code

    # 解析实名认证结果
    try:
        parsed_response = parse_id_verify_response_v2(response.text)
        result_xm = parsed_response['result_xm']
        result_gmsfhm = parsed_response['result_gmsfhm']
        message = parsed_response['message'] or u'未知错误'
        if result_xm and result_gmsfhm:
            if result_xm == u'一致' == result_gmsfhm:
                verify_result = True
                id_photo = parsed_response['id_photo']
                message = u"成功" if id_photo else message
            else:
                logger.error("id_number==>[%s], result_xm==>[%s, %s], result_gmsfhm==>[%s, %s]"
                             " validate faild" % (id_number, result_xm, type(result_xm),
                                                  result_gmsfhm, type(result_gmsfhm)))
                message = u"姓名不一致"
    except Exception, e:
        logger.error("reponse_text==>[%s]validate failed" % response.text)
        logger.error(e)
        message = u"解析错误"

    return verify_result, id_photo, message


def parse_id_verify_response(text):
    import xml.etree.ElementTree as ETree

    root = ETree.fromstring(text.encode('utf-8'))
    response_code = int(next(root.iter('{http://schemas.datacontract.org/2004/07/Finance.EPM}ResponseCode')).text)
    result_text = next(root.iter('{http://schemas.datacontract.org/2004/07/Finance.EPM}Result')).text

    return {
        'response_code': response_code,
        'result': result_text,
    }
