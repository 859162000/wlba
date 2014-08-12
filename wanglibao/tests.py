# coding=utf-8
from django.test import TestCase
from wanglibao.templatetags.formatters import number_to_chinese


class Test(TestCase):
    def testNumberFormatter(self):
        self.assertEqual(number_to_chinese(100), u'壹佰元整')
        self.assertEqual(number_to_chinese(1001), u'壹仟零壹元整')
        self.assertEqual(number_to_chinese(1001.12), u'壹仟零壹元壹角贰分')
        self.assertEqual(number_to_chinese(1000000000), u'壹拾亿元整')
        self.assertEqual(number_to_chinese(1203000400), u'壹拾贰亿零叁佰万零肆佰元整')

    def testNginxDumps(self):
        from vender.nginxparser import dumps

        output = dumps([
            ['server', [
                ['listen', '80'],
                ['server_name', 'foo.com'],
                ['root', '/home/ubuntu/sites/foo/'],
            ]],
        ])
        self.assertGreater(len(output), 0)
