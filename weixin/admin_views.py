# encoding:utf-8
from __future__ import unicode_literals
from django.views.generic import View, TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import SessionAuthentication
from .models import Account, Material, MaterialImage, MaterialNews
from wechatpy.client import WeChatClient
from weixin.wechatpy.exceptions import WeChatException
from functools import wraps


def weixin_api_error(f):
    @wraps(f)
    def decoration(*args, **kwargs):
        try:
            res = f(*args, **kwargs)
        except WeChatException, e:
            return Response(e.__dict__, status=400)
        return res
    return decoration


class AdminWeixinAccountMixin(object):
    account_cache = None
    client_cache = None

    def get_account(self, account_id=None):
        account_id = account_id or self.request.session.get('account_id')
        if not account_id:
            raise Http404()
        try:
            account = Account.objects.get(pk=int(account_id))
        except Account.DoesNotExist:
            raise Http404('page not found')
        return account

    @property
    def account(self):
        if not self.account_cache:
            self.account_cache = self.get_account()
        return self.account_cache

    @property
    def client(self):
        if not self.client_cache:
            self.client_cache = WeChatClient(self.account.app_id, self.account.app_secret, self.account.access_token)
        return self.client_cache


class AdminTemplateView(TemplateView):

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminTemplateView, self).dispatch(request, *args, **kwargs)


class AdminView(View):
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminView, self).dispatch(request, *args, **kwargs)


class AdminWeixinView(AdminView, AdminWeixinAccountMixin):
    pass


class AdminWeixinTemplateView(AdminTemplateView, AdminWeixinAccountMixin):
    pass


class AdminAPISessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        pass


class AdminAPIView(APIView, AdminWeixinAccountMixin):
    permission_classes = (IsAdminUser,)
    authentication_classes = (AdminAPISessionAuthentication,)


class WeixinView(AdminWeixinTemplateView):
    template_name = 'admin/weixin_manage.html'

    def get_context_data(self, id, **kwargs):
        context = super(WeixinView, self).get_context_data(**kwargs)
        self.request.session['account_id'] = id
        context['account'] = self.account
        return context


class WeixinMassView(AdminWeixinTemplateView):
    template_name = 'admin/weixin_mass.html'

    def get_context_data(self, **kwargs):
        context = super(WeixinMassView, self).get_context_data(**kwargs)
        context['account'] = self.account
        return context


class WeixinReplyView(AdminWeixinTemplateView):
    template_name = 'admin/weixin_reply.html'

    def get_context_data(self, **kwargs):
        context = super(WeixinReplyView, self).get_context_data(**kwargs)
        context['account'] = self.account
        return context


class WeixinMenuView(AdminWeixinTemplateView):
    template_name = 'admin/weixin_menu.html'

    def get_context_data(self, **kwargs):
        context = super(WeixinMenuView, self).get_context_data(**kwargs)
        context['account'] = self.account
        return context


class WeixinMaterialView(AdminWeixinTemplateView):
    template_name = 'admin/weixin_material.html'

    def get_context_data(self, **kwargs):
        context = super(WeixinMaterialView, self).get_context_data(**kwargs)
        context['account'] = self.account
        # 获取素材总数 缓存24小时
        context['material'], _ = Material.objects.get_or_create(account=self.account)
        try:
            context.get('material').init()
        except WeChatException, e:
            return HttpResponseBadRequest(e)

        return context


class WeixinCustomerServiceView(AdminWeixinTemplateView):
    template_name = 'admin/weixin_customer_service.html'

    def get_context_data(self, **kwargs):
        context = super(WeixinCustomerServiceView, self).get_context_data(**kwargs)
        context['account'] = self.account
        return context


class WeixinCustomerServiceCreateView(AdminWeixinTemplateView):
    template_name = 'admin/weixin_customer_service_create.html'

    def get_context_data(self, **kwargs):
        context = super(WeixinCustomerServiceCreateView, self).get_context_data(**kwargs)
        context['account'] = self.account
        return context


class WeixinMaterialImageView(AdminWeixinView):

    def get(self, request, media_id):
        media = MaterialImage.objects.get(account=self.account, media_id=media_id)
        if not media.file:
            try:
                res = self.client.material.get(media_id)
            except WeChatException, e:
                return Response(e.__dict__, status=400)
            print dir(res)
            print res.content
            return HttpResponse(res.content, 'image/png')
            # if res.status_code == 200:
            #     if res.get('errcode'):
            #         return HttpResponseForbidden(res.json.get('errmsg'))
            #     # 图片存储到模型
            #     from PIL import ImageFile
            #     parser = ImageFile.Parser()
            #     media.file = ''
            # else:
            #     return Response(status=400)
        # return HttpResponseRedirect(reverse('admin_weixin_material_file', kwargs={'path', media.file}))


class WeixinMaterialListJsonApi(AdminAPIView):
    """
    获取素材列表接口
    type: voice, video, image, news
    page: int
    count: int 1-20 default 20
    """
    http_method_names = ['get']

    @weixin_api_error
    def get(self, request):
        media_type = request.GET.get('media_type')
        page = int(request.GET.get('page', '1'))
        count = int(request.GET.get('count', '20'))
        offset = count * (page - 1)

        res = self.client.material.batchget(media_type, offset, count)
        media_count = getattr(self.account.material, '{media_type}_count'.format(media_type=media_type))

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
            media_class.objects.filter(account=self.account).delete()

        for item in res.get('item'):
            try:
                media_class.objects.get(media_id=item.get('media_id'))
            except media_class.DoesNotExist:
                if media_type == 'image':
                    media_class.objects.create(
                        media_id=item.get('media_id'),
                        name=item.get('name'),
                        update_time=item.get('update_time'),
                        account=self.account
                    )
                elif media_type == 'news':
                    pass
                elif media_type == 'voice':
                    pass
                elif media_type == 'video':
                    pass

            res.get('item_count')

        return Response(res)


class WeixinCustomerServiceApi(AdminAPIView):

    http_method_names = ['post']

    @weixin_api_error
    def post(self, request):
        kf_account = '{}@gh_d852bc2cead2'.format(request.POST.get('kf_account'))
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')
        res = self.client.customservice.add_account(kf_account, nickname, password)
        return Response(res.json())


class WeixinMenuApi(AdminAPIView):
    http_method_names = ['get', 'post', 'delete']

    @weixin_api_error
    def get(self, request):
        key = 'account_menu_{account_id}'.format(account_id=self.account.id)
        if not cache.get(key):
            res = self.client.menu.get()
            try:
                menu = res.get('menu')
            except:
                menu = {'button': []}

            cache.set(key, menu, 60 * 60 * 24 / 10000)
        return Response(cache.get(key))

    @weixin_api_error
    def post(self, request):
        print request._is_secure()
        from django.core.urlresolvers import reverse
        print request.build_absolute_uri(reverse('weixin_oauth_login_redirect'))
        res = self.client.menu.create(request.body)
        return Response(res, status=201)

    @weixin_api_error
    def delete(self, request):
        res = self.client.menu.delete()
        return Response(res, status=204)