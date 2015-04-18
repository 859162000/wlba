# _*_ coding: utf-8 _*_

__author__ = 'zhanghe'

from django.core.urlresolvers import RegexURLResolver
from django.conf.urls import url
from django.utils import timezone
from wanglibao_activity.models import WapActivityTemplates
from django.template.response import TemplateResponse
import rendering
from rendering import *


def compose_decorators(decorators, wrappee):
    for wrapper in decorators:
        wrappee = wrapper(wrappee)
    return wrappee


def decorator_url(urlconf, *decorators):
    revdecorators = decorators[::-1]

    return url(
        urlconf._regex,
        compose_decorators(revdecorators, urlconf.callback),
        urlconf.default_args,
        urlconf.name
    )


def decorator_include(urlpatterns, *decorators):
    urls = []
    for urlconf in urlpatterns[0].urlpatterns:
        if not isinstance(urlconf, RegexURLResolver):
            urls.append(decorator_url(urlconf, *decorators))
        else:
            urls.append(decorator_include(urlconf, *decorators))

    return (urls, ) + urlpatterns[1:]


def wap_activity_manage(function, *args, **kwargs):
    """ 重新指定模板渲染wap活动页面 """
    def decorator(request):
        now = timezone.now()
        wap_activity = WapActivityTemplates.objects.filter(is_used=True, start_at__lte=now, end_at__gte=now, url=request.path).first()
        if wap_activity:
            template_name = wap_activity.aim_template
            if wap_activity.is_rendering and wap_activity.func_rendering in rendering.__all__:
                # 需要使用自定义渲染的函数
                kwargs.update(eval(wap_activity.func_rendering)(request))
            return TemplateResponse(request, template=template_name, context=kwargs)
        else:
            return function(request, *args, **kwargs)

    return decorator