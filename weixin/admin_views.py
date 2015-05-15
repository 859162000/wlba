# encoding:utf-8
from __future__ import unicode_literals
from django.views.generic import View, TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.core.cache import cache
from .models import Account, Material, MaterialImage, MaterialNews
from wechatpy.client import WeChatClient
import json


class AdminTemplateView(TemplateView):

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminTemplateView, self).dispatch(request, *args, **kwargs)


class AdminWeixinTemplateView(AdminTemplateView):

    def get_account(self, id=None):
        account_id = id or self.request.session.get('account_id')
        try:
            account = Account.objects.get(pk=account_id)
        except Account.DoesNotExist:
            raise Http404('page not found')
        return account


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

    def get_account(self, account_id=None):
        account_id = account_id or self.request.session.get('account_id')
        try:
            account = Account.objects.get(pk=account_id)
        except Account.DoesNotExist:
            raise Http404('page not found')
        return account

    @property
    def weixin_client(self):
        if not self.client:
            self.client = WeChatClient(self.account.app_id, self.account.app_secret, self.account.access_token)
        return self.client

    def render_json(self, data):
        return HttpResponse(json.dumps(data), 'application/json')


class WeixinView(AdminWeixinTemplateView):
    template_name = 'admin/weixin_manage.html'

    def get_context_data(self, id, **kwargs):
        context = super(WeixinView, self).get_context_data(**kwargs)
        context['account'] = self.get_account(id)
        self.request.session['account_id'] = id
        return context


class WeixinMassView(AdminWeixinTemplateView):
    template_name = 'admin/weixin_mass.html'

    def get_context_data(self, id, **kwargs):
        context = super(WeixinMassView, self).get_context_data(**kwargs)
        context['account'] = self.get_account(id)
        return context


class WeixinReplyView(AdminWeixinTemplateView):
    template_name = 'admin/weixin_reply.html'

    def get_context_data(self, id, **kwargs):
        context = super(WeixinReplyView, self).get_context_data(**kwargs)
        context['account'] = self.get_account(id)
        return context


class WeixinMenuView(AdminWeixinTemplateView):
    template_name = 'admin/weixin_menu.html'

    def get_context_data(self, id, **kwargs):
        context = super(WeixinMenuView, self).get_context_data(**kwargs)
        account = self.get_account(id)

        key = 'account_menu_{account_id}'.format(account_id=account.id)
        if not cache.get(key):
            menu = {'button': []}

            try:
                client = WeChatClient(account.app_id, account.app_secret, account.access_token)
                res = client.menu.get()
                if not res.get('errcode'):
                    menu = res.get('menu')
            except:
                pass

            cache.set(key, json.dumps(menu), 60 * 60 * 24 / 10000)

        context['menu'] = cache.get(key)
        context['account'] = account
        return context


class WeixinMaterialView(AdminWeixinTemplateView):
    template_name = 'admin/weixin_material.html'

    def get_context_data(self, id, **kwargs):
        context = super(WeixinMaterialView, self).get_context_data(**kwargs)
        context['account'] = self.get_account(id)
        # 获取素材总数 缓存24小时
        context['material'] = Material.objects.get_or_create(account=context.get('account'))
        context.get('material').init()

        return context


class WeixinCustomerServiceView(AdminWeixinTemplateView):
    template_name = 'admin/weixin_customer_service.html'

    def get_context_data(self, id, **kwargs):
        context = super(WeixinCustomerServiceView, self).get_context_data(**kwargs)
        context['account'] = self.get_account(id)
        return context


class WeixinCustomerServiceCreateView(AdminWeixinTemplateView):
    template_name = 'admin/weixin_customer_service_create.html'

    def get_context_data(self, id, **kwargs):
        context = super(WeixinCustomerServiceCreateView, self).get_context_data(**kwargs)
        context['account'] = self.get_account(id)
        return context


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


class WeixinCustomerServiceCreateApi(AdminJsonApi):

    def post(self, request, id):
        account = self.get_account(id)

        kf_account = '{}@gh_d852bc2cead2'.format(request.POST.get('kf_account'))
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')

        client = WeChatClient(account.app_id, account.app_secret, account.access_token)
        res = client.customservice.add_account(kf_account, nickname, password)
        return self.render_json(res.json())


class WeixinMenuCreateApi(AdminJsonApi):

    def post(self, request):
        account = self.get_account()
        client = WeChatClient(account.app_id, account.app_secret, account.access_token)
        res = client.menu.create(request.body)
        return self.render_json(res)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WeixinMenuCreateApi, self).dispatch(request, *args, **kwargs)


class WeixinMenuDeleteApi(AdminJsonApi):

    def post(self, request):
        account = self.get_account()
        client = WeChatClient(account.app_id, account.app_secret, account.access_token)
        res = client.menu.delete()
        return self.render_json(res)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(WeixinMenuDeleteApi, self).dispatch(request, *args, **kwargs)