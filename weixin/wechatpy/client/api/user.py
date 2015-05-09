# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from weixin.wechatpy.client.api.base import BaseWeChatAPI


class WeChatUser(BaseWeChatAPI):

    def get(self, user_id, lang='zh_CN'):
        """
        获取用户基本信息
        详情请参考
        http://mp.weixin.qq.com/wiki/14/bb5031008f1494a59c6f71fa0f319c66.html

        :param user_id: 用户 ID 。 就是你收到的 `Message` 的 source
        :param lang: 返回国家地区语言版本，zh_CN 简体，zh_TW 繁体，en 英语
        :return: 返回的 JSON 数据包
        """
        assert lang in ('zh_CN', 'zh_TW', 'en'), 'lang can only be one of \
            zh_CN, zh_TW, en language codes'
        return self._get(
            'user/info',
            params={
                'openid': user_id,
                'lang': lang
            }
        )

    def get_followers(self, first_user_id=None):
        """
        获取关注者列表
        详情请参考
        http://mp.weixin.qq.com/wiki/3/17e6919a39c1c53555185907acf70093.html

        :param first_user_id: 可选。第一个拉取的 OPENID，不填默认从头开始拉取
        :return: 返回的 JSON 数据包
        """
        params = {}
        if first_user_id:
            params['next_openid'] = first_user_id
        return self._get(
            'user/get',
            params=params
        )

    def update_remark(self, user_id, remark):
        """
        设置用户备注名
        详情请参考
        http://mp.weixin.qq.com/wiki/10/bf8f4e3074e1cf91eb6518b6d08d223e.html

        :param user_id: 用户 ID 。 就是你收到的 `Message` 的 source
        :param remark: 备注名
        :return: 返回的 JSON 数据包
        """
        return self._post(
            'user/info/updateremark',
            data={
                'openid': user_id,
                'remark': remark
            }
        )
