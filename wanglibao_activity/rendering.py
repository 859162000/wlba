# _*_ coding: utf-8 _*_

__author__ = 'zhanghe'


from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from django.utils import timezone
from marketing.models import PromotionToken
from models import WapActivityTemplates
from wanglibao_sms.utils import send_validation_code


def wap_activity_manage(function, *args, **kwargs):
    """ 重新指定模板渲染wap活动页面 """
    render_method = (
        'app_share_view',
        'app_share_reg_view',
    )

    def decorator(request):
        now = timezone.now()
        wap_activity = WapActivityTemplates.objects.filter(is_used=True, start_at__lte=now, end_at__gte=now, url=request.path).first()
        if wap_activity:
            template_name = wap_activity.aim_template
            if wap_activity.is_rendering and wap_activity.func_rendering in render_method:
                # 需要使用自定义渲染的函数
                kwargs.update(eval(wap_activity.func_rendering)(request))
                return TemplateResponse(request, template=template_name, context=kwargs)
            else:
                # 不需要更改渲染数据，只需重新指定模板
                for cell in function.func_closure:
                    if isinstance(cell.cell_contents, dict) and 'template_name' in cell.cell_contents:
                        cell.cell_contents.update({'template_name': template_name})
        return function(request, *args, **kwargs)

    return decorator


def app_share_view(request, *args, **kwargs):
    identifier = request.GET.get('phone')
    reg = request.GET.get('reg')
    return {
        'identifier': identifier,
        'reg': reg
    }


def app_share_reg_view(request, *args, **kwargs):
    identifier = request.GET.get('identifier')
    friend_identifier = request.GET.get('friend_identifier')

    if friend_identifier:
        try:
            user = User.objects.get(wanglibaouserprofile__phone=friend_identifier)
            promo_token = PromotionToken.objects.get(user=user)
            invitecode = promo_token.token
        except:
            invitecode = ''
    else:
        invitecode = ''

    send_validation_code(identifier)
    return {
        'identifier': identifier,
        'invitecode': invitecode
    }

