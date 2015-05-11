# encoding:utf-8
from __future__ import unicode_literals
from django.views.generic import View, TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from .models import Account, Material, MaterialImage, MaterialNews
from wechatpy.client import WeChatClient
import json


class AdminTemplateView(TemplateView):

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminTemplateView, self).dispatch(request, *args, **kwargs)


class AdminWeixinTemplateView(AdminTemplateView):

    def get_account(self, id):
        try:
            account = Account.objects.get(pk=id)
        except Account.DoesNotExist:
            raise Http404('page not found')
        return account


class WeixinView(AdminWeixinTemplateView):

    template_name = 'admin/weixin_manage.html'

    def get_context_data(self, id, **kwargs):
        account = self.get_account(id)
        print account.jsapi_ticket

        return {
            'account': account
        }


class WeixinMassView(AdminWeixinTemplateView):

    template_name = 'admin/weixin_mass.html'

    def get_context_data(self, id, **kwargs):
        account = self.get_account(id)

        return {
            'account': account
        }


class WeixinReplyView(AdminWeixinTemplateView):

    template_name = 'admin/weixin_reply.html'

    def get_context_data(self, id, **kwargs):

        account = self.get_account(id)

        return {
            'account': account
        }


class WeixinMenuView(AdminWeixinTemplateView):

    template_name = 'admin/weixin_menu.html'

    def get_context_data(self, id, **kwargs):
        account = self.get_account(id)
        return {
            'account': account
        }


class WeixinMaterialView(AdminWeixinTemplateView):

    template_name = 'admin/weixin_material.html'

    def get_context_data(self, id, **kwargs):
        account = self.get_account(id)
        # 获取素材总数 缓存24小时
        material = Material.objects.get_or_create(account=account)
        material.init()

        return {
            'account': account,
            'material': material
        }



class AdminView(View):
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminView, self).dispatch(request, *args, **kwargs)

    def get_account(self, id):
        try:
            account = Account.objects.get(pk=id)
        except Account.DoesNotExist:
            raise Http404('page not found')
        return account


class AdminJsonApi(AdminView):
    account = None
    client = None

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminJsonApi, self).dispatch(request, *args, **kwargs)

    def get_account(self, id):
        try:
            self.account = Account.objects.get(pk=id)
        except Account.DoesNotExist:
            raise Http404('page not found')
        return self.account

    @property
    def weixin_client(self):
        if not self.client:
            self.client = WeChatClient(self.account.app_id, self.account.app_secret, self.account.access_token)
        return self.client

    def render_json(self, data):

        return HttpResponse(json.dumps(data), 'application/json')


class WeixinMaterialListJsonApi(AdminJsonApi):
    """
    获取素材列表接口
    type: voice, video, image, news
    page: int
    count: int 1-20 default 20
    """

    def get(self, request, id):
        media_type = request.GET.get('media_type')
        page = int(request.GET.get('page', '1'))
        count = int(request.GET.get('count', '20'))
        offset = count * (page - 1)
        account = self.get_account(id)
        client = WeChatClient(account.app_id, account.app_secret, account.access_token)
        try:
            res = client.material.batchget(media_type, offset, count)
        except Exception, e:
            return self.render_json({'errcode': e.errcode, 'errmsg': e.errmsg})

        media_count = getattr(account.material, '{media_type}_count'.format(media_type=media_type))

        media_class_dict = {
            'image': MaterialImage,
            'news': MaterialNews,
            # 'voice': MaterialVoice,
            # 'video': MaterialVideo,
        }

        media_class = media_class_dict.get(media_type)
        # 如果第一次获取，并且本地数据于微信官方数据不一致 则清空数据库
        if offset == 0 and media_count != res.get('total_count'):
            # 清空数据库
            media_class.objects.filter(account=account).delete()

        for item in res.get('item'):
            try:
                media_class.objects.get(media_id=item.get('media_id'))
            except media_class.DoesNotExist:
                if media_type == 'image':
                    media_class.objects.create(
                        media_id=item.get('media_id'),
                        name=item.get('name'),
                        update_time=item.get('update_time'),
                        account=account
                    )
                elif media_type == 'news':
                    pass
                elif media_type == 'voice':
                    pass
                elif media_type == 'video':
                    pass

            res.get('item_count')

        return self.render_json(res)


class WeixinMaterialImageView(AdminView):

    def get(self, request, id, media_id):
        account = self.get_account(id)
        media = MaterialImage.objects.get(account=account, media_id=media_id)
        if not media.file:
            client = WeChatClient(account.app_id, account.app_secret, account.access_token)
            res = client.material.get(media_id)
            if res.status_code == 200:
                if res.json.get('errcode'):
                    return HttpResponseForbidden(res.json.get('errmsg'))
                # 图片存储到模型
                from PIL import ImageFile
                parser = ImageFile.Parser()
                media.file = ''
            else:
                return HttpResponseForbidden()
        return HttpResponseRedirect(reverse('weixin_material_file', kwargs={'path', media.file}))