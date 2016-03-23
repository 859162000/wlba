# encoding:utf8

from rest_framework.views import APIView
from rest_framework.response import Response
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_banner.filter import BannerFilterSet
from wanglibao_banner.models import Banner, Hiring
from wanglibao_banner.serializer import BannerSerializer
from django.views.generic import TemplateView
from wanglibao_rest import utils
from misc.models import Misc
from wanglibao_banner.models import Banner, Aboutus, AboutDynamic
from django.http import Http404
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


#class BannerViewSet(PaginatedModelViewSet):
#    """
#    广告条
#    """
#    model = Banner
#    serializer_class = BannerSerializer
#    filter_class = BannerFilterSet
#    permission_classes = (IsAdminUserOrReadOnly,)

class BannerViewSet(APIView):
    permission_classes = (IsAdminUserOrReadOnly,)

    def get(self, request):
        device = utils.split_ua(request)
        result = []
        device_t = "mobile"
        if device['device_type'] == "ios":
            dic = Misc.objects.filter(key="ios_hide_banner_version").first()
            try:
                dataver = dic.value.split(",")
                appver = device['app_version']
                if appver in dataver:
                    return Response({"ret_code":1, "results":result})
            except Exception, e:
                pass
        elif device['device_type'] == "pc":
            device_t = "PC_2"
        device_t = "mobile"
        # bans = Banner.objects.filter(device=device_t)
        bans = Banner.objects.filter(Q(device=device_t), Q(is_used=True), Q(is_long_used=True) | (Q(is_long_used=False) & Q(start_at__lte=timezone.now()) & Q(end_at__gte=timezone.now())))
        for x in bans:
            obj = {"id":x.id, "image":str(x.image), "link":x.link, "name":x.name,
                            "priority":x.priority, "type":x.type}
            if device_t == "mobile":
                if not x.alt:
                    result.append(obj)
                elif 'channel_id' in device and x.alt == device['channel_id']:
                    result.append(obj)
            else:
                result.append(obj)
        return Response({"ret_code":0, "results":result})
            

class HiringView(TemplateView):
    template_name = 'hiring.jade'

    def get_context_data(self, **kwargs):

        hiring = Hiring.objects.filter(is_hide=False).order_by('-priority')

        return {
            'hirings': hiring
        }


class AboutView(TemplateView):
    template_name = 'about_new.jade'

    def get_context_data(self, **kwargs):
        about_us = Aboutus.objects.filter(code='about').first()
        return {
            'about_us': about_us
        }


class CompanyView(TemplateView):
    template_name = 'company.jade'

    def get_context_data(self, **kwargs):
        about_us = Aboutus.objects.filter(code='company').first()
        return {
            'about_us': about_us
        }


class TeamView(TemplateView):
    template_name = 'team.jade'

    def get_context_data(self, **kwargs):
        about_us = Aboutus.objects.filter(code='team').first()
        return {
            'about_us': about_us
        }


class MilestoneView(TemplateView):
    template_name = 'milestone.jade'

    def get_context_data(self, **kwargs):
        about_us = Aboutus.objects.filter(code='milestone').first()
        return {
            'about_us': about_us
        }


class ResponsibilityView(TemplateView):
    template_name = 'responsibility.jade'

    def get_context_data(self, **kwargs):
        about_us = Aboutus.objects.filter(code='responsibility').first()
        return {
            'about_us': about_us
        }


class ContactView(TemplateView):
    template_name = 'contact_us.jade'

    def get_context_data(self, **kwargs):
        about_us = Aboutus.objects.filter(code='contact_us').first()
        return {
            'about_us': about_us
        }


class AgreementView(TemplateView):
    template_name = 'agreement.jade'

    def get_context_data(self, **kwargs):
        about_us = Aboutus.objects.filter(code='agreement').first()
        return {
            'about_us': about_us
        }


class DirectorateView(TemplateView):
    template_name = 'directorate.jade'

    def get_context_data(self, **kwargs):
        directorate = Aboutus.objects.filter(code='directorate').first()
        return {
            'directorate': directorate
        }


class AgreementAutoView(TemplateView):
    template_name = 'agreement.jade'

    def get_context_data(self, **kwargs):
        about_us = Aboutus.objects.filter(code='agreement_auto').first()
        return {
            'about_us': about_us
        }


class DynamicHomeView(TemplateView):
    template_name = 'milestone.jade'

    def get_context_data(self, **kwargs):
        about_dynamics = AboutDynamic.objects.filter(hide_in_list=False).order_by('-updated_time')

        about_dynamic_list = []
        about_dynamic_list.extend(about_dynamics)

        limit = 10
        page = self.request.GET.get('page', 1)

        if about_dynamic_list:
            paginator = Paginator(about_dynamic_list, limit)
            try:
                about_dynamic_list = paginator.page(page)
            except PageNotAnInteger:
                about_dynamic_list = paginator.page(1)
            except EmptyPage:
                about_dynamic_list = []
            except Exception:
                about_dynamic_list = paginator.page(paginator.num_pages)

            count = paginator.num_pages
        else:
            about_dynamic_list = []
            count = 0

        return {
            'data': about_dynamic_list,
            'page': page,
            'num': limit,
            'count': count
        }


class DynamicDetailView(TemplateView):
    template_name = 'milestone_detail.jade'

    def get_context_data(self, id, **kwargs):
        try:
            dynamic = AboutDynamic.objects.get(pk=id, hide_in_list=False)
        except AboutDynamic.DoesNotExist:
            raise Http404(u'您查找的公告不存在')

        return {
            'data': dynamic
        }
