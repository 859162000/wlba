# encoding:utf-8
from __future__ import unicode_literals
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import SessionAuthentication
from weixin.common.decorators import weixin_api_error
from weixin.common.wx import get_host_url
from weixin.models import WeixinAccounts, Material


class ManageAccountMixin(object):
    account_cache = None
    client_cache = None

    def get_account(self, account_key=None):
        try:
            account_key = account_key or self.request.session.get('account_key')
            account = WeixinAccounts.get(account_key)
            return account
        except:
            raise Http404()

    @property
    def account(self):
        if not self.account_cache:
            self.account_cache = self.get_account()
        return self.account_cache

    @property
    def client(self):
        return self.account.weixin_client


class ManageAPISessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        pass


class ManageAPIView(APIView, ManageAccountMixin):
    permission_classes = (IsAdminUser,)
    authentication_classes = (ManageAPISessionAuthentication,)


class ManageView(TemplateView, ManageAccountMixin):

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ManageView, self).dispatch(request, *args, **kwargs)


class IndexView(ManageView):
    template_name = 'manage/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        WeixinAccounts.host_url = get_host_url(self.request)
        context['items'] = WeixinAccounts.all()
        if True:
            WeixinAccounts.syncdb()
        return context


class AccountView(ManageView):
    template_name = 'manage/account.html'

    def get_context_data(self, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs)
        self.request.session['account_key'] = kwargs.get('account_key')
        context['account'] = self.account

        return context


class MenuView(ManageView):
    template_name = 'manage/menu.html'

    def get_context_data(self, **kwargs):
        context = super(MenuView, self).get_context_data(**kwargs)
        context['account'] = self.account
        return context


class MaterialView(ManageView):
    template_name = 'manage/material.html'

    def get_context_data(self, **kwargs):
        context = super(MaterialView, self).get_context_data(**kwargs)
        context['account'] = self.account
        return context


class MaterialImageView(View, ManageAccountMixin):

    def get(self, request, media_id):
        account = self.get_account()
        res = account.weixin_client.media.download(media_id)
        print res
        print res.content
        return HttpResponse('123')


class MenuAPI(ManageAPIView):

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
        res = self.client.menu.create(request.body)
        return Response(res, status=201)

    @weixin_api_error
    def delete(self, request):
        res = self.client.menu.delete()
        return Response(res, status=204)


class MaterialListAPI(ManageAPIView):

    @weixin_api_error
    def get(self, request):
        media_type = request.GET.get('media_type')
        offset = int(request.GET.get('offset', 0))
        count = int(request.GET.get('count', 20))
        res = self.client.material.batchget(media_type, offset, count)
        return Response(res)

    @weixin_api_error
    def post(self, request):
        media_type = request.POST.get('media_type')
        if media_type == 'news':
            article = request.POST.get('article')
            res = self.client.material.add_articles(article)
        else:
            media_file = request.FILES.get('media_file')
            title = request.POST.get('title')
            introduction = request.POST.get('introduction')
            res = self.client.material.add(media_type, media_file, title, introduction)
        return Response(res, status=201)


class MaterialCountAPI(ManageAPIView):

    @weixin_api_error
    def get(self, request):
        account = self.get_account()
        try:
            material = account.db_account.material
        except Material.DoesNotExist:
            material, _ = Material.objects.get_or_create(account=account.db_account)

        # 判断数据是否过期
        if material.is_expires_in():
            res = material.data()
        else:
            res = self.client.material.get_count()
            material.update_data(res, account.material_count_cache_time)

        return Response(res)


class MaterialDetailAPI(ManageAPIView):

    @weixin_api_error
    def get(self, request, media_id):
        res = self.client.material.get(media_id)
        return Response(res)

    @weixin_api_error
    def post(self, request, media_id):
        """
        {
          "media_id":MEDIA_ID,
          "index":INDEX,
          "articles": {
               "title": TITLE,
               "thumb_media_id": THUMB_MEDIA_ID,
               "author": AUTHOR,
               "digest": DIGEST,
               "show_cover_pic": SHOW_COVER_PIC(0 / 1),
               "content": CONTENT,
               "content_source_url": CONTENT_SOURCE_URL
            }
        }

        :param request:
        :param media_id:
        :return:
        """
        index = request.POST.get('index')
        articles = request.POST.get('articles')
        res = self.client.material.update_articles(media_id, index, articles)
        return Response(res)

    @weixin_api_error
    def delete(self, request, media_id):
        res = self.client.material.delete(media_id)
        return Response(res, status=204)

