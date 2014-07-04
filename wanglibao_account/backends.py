# coding=utf-8
import logging
from django.conf import settings
import requests
from wanglibao_account.models import IdVerification

logger = logging.getLogger(__name__)


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

        parsed_response = parse_id_verify_response(response.text)
        result = bool(parsed_response['response_code'] == 100)

        if not result:
            logger.error("Failed to validate: %s" % response.text)

        verify_result = True
        if parsed_response['result'] != u'一致':
            verify_result = False
            logger.info("Identity not consistent %s" % response.text)

        record = IdVerification(id_number=id_number, name=name, is_valid=verify_result)
        record.save()

        return record, None


def parse_id_verify_response(text):
    import xml.etree.ElementTree as ETree

    root = ETree.fromstring(text.encode('utf-8'))
    response_code = int(next(root.iter('{http://schemas.datacontract.org/2004/07/Finance.EPM}ResponseCode')).text)
    result_text = next(root.iter('{http://schemas.datacontract.org/2004/07/Finance.EPM}Result')).text

    return {
        'response_code': response_code,
        'result': result_text,
    }