from django.test import TestCase
from views import WeiXin
import unittest

class WeiXinTestCase(unittest.TestCase):
    def test_gen_signature(self):
        params = {
            'token':'token',
            'timestamp':'timestamp',
            'nonce':'nonce',
        }
        gen_signature = WeiXin.gen_signature(params)
        self.assertEqual('6db4861c77e0633e0105672fcd41c9fc2766e26e', gen_signature)

    def test_on_connect_validate(self):
        weixin = WeiXin.on_connect(token='token',
            timestamp='timestamp',
            nonce='nonce',
            signature='6db4861c77e0633e0105672fcd41c9fc2766e26e',
            echostr='echostr')
        self.assertEqual(weixin.validate(), True)

    def test_on_connect_validate_false(self):
        weixin = WeiXin.on_connect(token='token',
            timestamp='timestamp',
            nonce='nonce_false',
            signature='6db4861c77e0633e0105672fcd41c9fc2766e26e',
            echostr='echostr')
        self.assertEqual(weixin.validate(), False)

    def test_on_message_text(self):
        body = '''
        <xml>
            <ToUserName><![CDATA[toUser]]></ToUserName>
            <FromUserName><![CDATA[fromUser]]></FromUserName>
            <CreateTime>1348831860</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[this is a test]]></Content>
            <MsgId>1234567890123456</MsgId>
       </xml>
        '''
        weixin = WeiXin.on_message(body)
        j = weixin.to_json()
        def assertParam(name, value):
            self.assertEqual(name in j, True)
            self.assertEqual(j[name], value)
        assertParam('ToUserName', 'toUser')
        assertParam('FromUserName', 'fromUser')
        assertParam('CreateTime', 1348831860)
        assertParam('MsgType', 'text')
        assertParam('Content', 'this is a test')
        assertParam('MsgId', '1234567890123456')

    def test_on_message_image(self):
        body = '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[image]]></MsgType>
        <PicUrl><![CDATA[this is a url]]></PicUrl>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        weixin = WeiXin.on_message(body)
        j = weixin.to_json()
        def assertParam(name, value):
            self.assertEqual(name in j, True)
            self.assertEqual(j[name], value)
        assertParam('ToUserName', 'toUser')
        assertParam('FromUserName', 'fromUser')
        assertParam('CreateTime', 1348831860)
        assertParam('MsgType', 'image')
        assertParam('PicUrl', 'this is a url')
        assertParam('MsgId', '1234567890123456')

    def test_on_message_location(self):
        body = '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1351776360</CreateTime>
        <MsgType><![CDATA[location]]></MsgType>
        <Location_X>23.134521</Location_X>
        <Location_Y>113.358803</Location_Y>
        <Scale>20</Scale>
        <Label><![CDATA[位置信息]]></Label>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        weixin = WeiXin.on_message(body)
        j = weixin.to_json()
        def assertParam(name, value):
            self.assertEqual(name in j, True)
            self.assertEqual(j[name], value)
        assertParam('ToUserName', 'toUser')
        assertParam('FromUserName', 'fromUser')
        assertParam('CreateTime', 1351776360)
        assertParam('MsgType', 'location')
        assertParam('Location_X', '23.134521')
        assertParam('Location_Y', '113.358803')
        assertParam('Scale', '20')
        assertParam('Label', u'位置信息')
        assertParam('MsgId', '1234567890123456')

    def test_on_message_link(self):
        body = '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>1351776360</CreateTime>
        <MsgType><![CDATA[link]]></MsgType>
        <Title><![CDATA[公众平台官网链接]]></Title>
        <Description><![CDATA[公众平台官网链接]]></Description>
        <Url><![CDATA[url]]></Url>
        <MsgId>1234567890123456</MsgId>
        </xml>
        '''
        weixin = WeiXin.on_message(body)
        j = weixin.to_json()
        def assertParam(name, value):
            self.assertEqual(name in j, True)
            self.assertEqual(j[name], value)
        assertParam('ToUserName', 'toUser')
        assertParam('FromUserName', 'fromUser')
        assertParam('CreateTime', 1351776360)
        assertParam('MsgType', 'link')
        assertParam('Title', u'公众平台官网链接')
        assertParam('Description', u'公众平台官网链接')
        assertParam('Url', 'url')
        assertParam('MsgId', '1234567890123456')

    def test_to_xml_text(self):
        xml = '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[fromUser]]></FromUserName>
        <CreateTime>12345678</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[content]]></Content>
        <FuncFlag>0</FuncFlag>
        </xml>
        '''
        weixin = WeiXin()
        to_user_name = 'toUser'
        from_user_name = 'fromUser'
        create_time = 12345678
        msg_type = 'text'
        content = 'content'
        func_flag = 0
        self.assertEqual(xml.replace('\n', '').replace(' ', '').strip(), weixin.to_xml(to_user_name=to_user_name,
            from_user_name=from_user_name,
            create_time=create_time,
            msg_type=msg_type,
            content=content,
            func_flag=func_flag))

if __name__ == '__main__':
    unittest.main()