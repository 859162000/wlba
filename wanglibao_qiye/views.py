# encoding:utf-8

import json
import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.views.generic import TemplateView
from django.http import HttpResponse
from file_storage.storages import AliOSSStorageForCover
from wanglibao_pay.models import Bank
from .models import EnterpriseUserProfile
from .forms import EnterpriseUserProfileForm

logger = logging.getLogger(__name__)


def get_have_company_channel_banks():
    return Bank.objects.filter(have_company_channel=True)


class QiYeIndex(TemplateView):
    template_name = 'qiye_register.jade'


class QiYeInfo(TemplateView):
    template_name = 'info.jade'

    def get_context_data(self, **kwargs):
        return {
            'banks': get_have_company_channel_banks(),
        }


class EnterpriseProfileUploadApi(APIView):
    """企业用户认证扩展资料接收接口"""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        if user.wanglibaouserprofile.utype == '3':
            field_name = request.POST.get('field_name')
            if field_name in ('business_license', 'registration_cert') and field_name in request.FILES:
                e_profile = EnterpriseUserProfile.objects.filter(user=user).first()
                # 判断企业信息是否审核中，如果是则不允许修改
                if e_profile and e_profile.status in (u'审核中', u'待审核'):
                    response_data = {
                        'filename': None,
                        'message': u'企业信息审核中，不能更改',
                        'ret_code': 30002,
                    }
                else:
                    file_name = request.POST.get('name', '')
                    file_suffix = file_name.split('.')[-1] or 'png'
                    filename = 'enterprise/images/%s_%s.%s' % (user.id, field_name, file_suffix)
                    file_content = request.FILES[field_name]

                    try:
                        AliOSSStorageForCover().save(filename, file_content)
                    except Exception, e:
                        logger.info('aliyun save faild with user[%s], fieldname[%s]' % (user.id, filename))
                        logger.info(e)

                        response_data = {
                            'filename': None,
                            'message': u'上传失败',
                            'ret_code': 40001,
                        }
                    else:
                        if e_profile:
                            e_profile.status = u'待审核'
                            e_profile.save()

                        user.wanglibaouserprofile.id_is_valid = False
                        user.wanglibaouserprofile.save()

                        response_data = {
                            'filename': filename,
                            'message': 'success',
                            'ret_code': 10000,
                        }

                        return HttpResponse(json.dumps(response_data), status=200, content_type='application/json')
            else:
                response_data = {
                    'filename': None,
                    'message': u'无效参数field_name',
                    'ret_code': 30001,
                }
        else:
            response_data = {
                'filename': None,
                'message': u'非企业用户',
                'ret_code': 20001,
            }

        return HttpResponse(json.dumps(response_data), status=400, content_type='application/json')


class GetEnterpriseUserProfileApi(APIView):
    """企业用户认证资料获取接口"""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        if user.wanglibaouserprofile.utype == '3':
            try:
                e_profile = EnterpriseUserProfile.objects.values().filter(user=user).first()
                del e_profile['modify_time']
                del e_profile['created_time']
                response_data = {
                    'data': e_profile,
                    'message': 'success',
                    'ret_code': 10000
                }
                return HttpResponse(json.dumps(response_data), status=200, content_type='application/json')
            except EnterpriseUserProfile.DoesNotExist:
                response_data = {
                    'data': None,
                    'message': u'企业用户信息未完善',
                    'ret_code': 10001
                }
        else:
            response_data = {
                'data': None,
                'message': u'非企业用户',
                'ret_code': 20001,
            }

        return HttpResponse(json.dumps(response_data), status=400, content_type='application/json')


class EnterpriseProfileCreateApi(APIView):
    """企业用户认证资料接收接口"""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        if user.wanglibaouserprofile.utype == '3':
            form = EnterpriseUserProfileForm('create', request.user, request.POST)
            if form.is_valid():
                if EnterpriseUserProfile.objects.filter(user=user).first():
                    response_data = {
                        'message': u'企业用户信息已存在',
                        'ret_code': 10002,
                    }
                else:
                    e_profile = EnterpriseUserProfile()
                    e_profile.user = user
                    e_profile.company_name = form.cleaned_data['company_name']
                    e_profile.business_license = form.cleaned_data['business_license']
                    e_profile.registration_cert = form.cleaned_data['registration_cert']
                    e_profile.certigier_name = form.cleaned_data['certigier_name']
                    e_profile.certigier_phone = form.cleaned_data['certigier_phone']
                    e_profile.company_address = form.cleaned_data['company_address']
                    e_profile.bank_card_no = form.cleaned_data['company_account']
                    e_profile.bank_account_name = form.cleaned_data['company_account_name']
                    e_profile.deposit_bank_province = form.cleaned_data['deposit_bank_province']
                    e_profile.deposit_bank_city = form.cleaned_data['deposit_bank_city']
                    e_profile.bank_branch_address = form.cleaned_data['bank_branch_address']
                    e_profile.bank = form.cleaned_data['bank']
                    e_profile.save()

                    user.wanglibaouserprofile.trade_pwd = form.cleaned_data['trade_pwd']
                    user.wanglibaouserprofile.save()

                    response_data = {
                        'message': u'提交成功',
                        'ret_code': 10000,
                    }
                    return HttpResponse(json.dumps(response_data), status=200, content_type='application/json')
            else:
                form_errors = form.errors
                form_error_keys = form_errors.keys()
                form_errors_list = []
                for key in form_error_keys:
                    value = form_errors[key]
                    form_error = u'、'.join(value)
                    form_errors_list.append(form_error)

                response_data = {
                    'message': u'表单错误：' + u'、'.join(form_errors_list),
                    'ret_code': 10001,
                }
        else:
            response_data = {
                'message': u'非企业用户',
                'ret_code': 20001,
            }

        return HttpResponse(json.dumps(response_data), status=400, content_type='application/json')


class EnterpriseProfileEditView(TemplateView):
    """企业用户认证资料修改视图"""

    template_name = 'update.jade'

    def get_context_data(self, **kwargs):
        user = self.request.user
        if user.wanglibaouserprofile.utype == '3':
            try:
                e_profile = EnterpriseUserProfile.objects.get(user=user)
                e_profile.banks = get_have_company_channel_banks()
                e_profile.trade_pwd = user.wanglibaouserprofile.trade_pwd
                response_data = {
                    'data': e_profile,
                    'message': 'success',
                    'ret_code': 10000
                }
            except EnterpriseUserProfile.DoesNotExist:
                response_data = {
                    'data': None,
                    'message': u'企业用户信息未完善',
                    'ret_code': 10001
                }
        else:
            response_data = {
                'data': None,
                'message': u'非企业用户',
                'ret_code': 20001,
            }

        return response_data


class EnterpriseProfileUpdateApi(APIView):
    """企业用户认证资料接收接口"""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        if user.wanglibaouserprofile.utype == '3':
            form = EnterpriseUserProfileForm('update', request.user, request.POST)
            if form.is_valid():
                try:
                    e_profile = EnterpriseUserProfile.objects.get(user=user)
                except EnterpriseUserProfile.DoesNotExist:
                    response_data = {
                        'message': u'企业用户信息未完善',
                        'ret_code': 10001,
                    }
                else:
                    # 判断企业信息是否审核中，如果是则不允许修改
                    if e_profile.status in (u'审核中', u'待审核'):
                        response_data = {
                            'filename': None,
                            'message': u'企业信息审核中，不能更改',
                            'ret_code': 30002,
                        }
                    else:
                        form_data = form.cleaned_data
                        profile_has_changed = False
                        change_list = []

                        if e_profile.company_name != form_data['company_name']:
                            e_profile.company_name = form_data['company_name']
                            change_list.append(u'[公司名称]')
                            profile_has_changed = True

                        if e_profile.business_license != form_data['business_license']:
                            e_profile.business_license = form_data['business_license']
                            change_list.append(u'[公司营业执照]')
                            profile_has_changed = True

                        if e_profile.registration_cert != form_data['registration_cert']:
                            e_profile.registration_cert = form_data['registration_cert']
                            change_list.append(u'[公司税务登记证]')
                            profile_has_changed = True

                        if e_profile.certigier_name != form_data['certigier_name']:
                            e_profile.certigier_name = form_data['certigier_name']
                            change_list.append(u'[授权人姓名]')
                            profile_has_changed = True

                        if e_profile.certigier_phone != form_data['certigier_phone']:
                            e_profile.certigier_phone = form_data['certigier_phone']
                            change_list.append(u'[授权人手机号]')
                            profile_has_changed = True

                        if e_profile.company_address != form_data['company_address']:
                            e_profile.company_address = form_data['company_address']
                            change_list.append(u'[公司地址]')
                            profile_has_changed = True

                        if user.wanglibaouserprofile.trade_pwd != form_data['trade_pwd']:
                            user.wanglibaouserprofile.trade_pwd = form_data['trade_pwd']
                            user.wanglibaouserprofile.save()
                            change_list.append(u'[交易密码]')
                            profile_has_changed = True

                        if e_profile.status == u'审核失败' and not user.wanglibaouserprofile.id_valid_time:
                            if e_profile.bank_card_no != form_data['company_account']:
                                e_profile.bank_card_no = form_data['company_account']
                                change_list.append(u'[公司账户账号]')
                                profile_has_changed = True

                            if e_profile.bank_account_name != form_data['company_account_name']:
                                e_profile.bank_account_name = form_data['company_account_name']
                                change_list.append(u'[公司账户名称]')
                                profile_has_changed = True

                            if e_profile.deposit_bank_province != form_data['deposit_bank_province']:
                                e_profile.deposit_bank_province = form_data['deposit_bank_province']
                                change_list.append(u'[公司开户行所在省份]')
                                profile_has_changed = True

                            if e_profile.deposit_bank_city != form_data['deposit_bank_city']:
                                e_profile.deposit_bank_city = form_data['deposit_bank_city']
                                change_list.append(u'[公司开户行所在市县]')
                                profile_has_changed = True

                            if e_profile.bank_branch_address != form_data['bank_branch_address']:
                                e_profile.bank_branch_address = form_data['bank_branch_address']
                                change_list.append(u'[开户行支行所在地]')
                                profile_has_changed = True

                            if e_profile.bank != form_data['bank']:
                                e_profile.bank = form_data['bank']
                                change_list.append(u'[所属银行]')
                                profile_has_changed = True

                        # FixMe,交易码变更是否需要重新审核
                        if profile_has_changed:
                            e_profile.description = u'待审核字段:' + u'、'.join(change_list)
                            e_profile.status = u'待审核'
                            e_profile.save()
                            user.wanglibaouserprofile.save()

                        response_data = {
                            'message': 'success',
                            'ret_code': 10000,
                        }
                        return HttpResponse(json.dumps(response_data), status=200, content_type='application/json')
            else:
                form_errors = form.errors
                form_error_keys = form_errors.keys()
                form_errors_list = []
                for key in form_error_keys:
                    value = form_errors[key]
                    form_error = u'、'.join(value)
                    form_errors_list.append(form_error)

                response_data = {
                    'message': u'表单错误：' + u'、'.join(form_errors_list),
                    'ret_code': 10001,
                }
        else:
            response_data = {
                'message': u'非企业用户',
                'ret_code': 20001,
            }

        return HttpResponse(json.dumps(response_data), status=400, content_type='application/json')


class EnterpriseProfileIsExistsApi(APIView):
    """
    判断企业用户是否已经完善企业信息
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        if user.wanglibaouserprofile.utype == '3':
            try:
                EnterpriseUserProfile.objects.get(user=user)
            except EnterpriseUserProfile.DoesNotExist:
                response_data = {
                    'message': u'企业用户信息未完善',
                    'ret_code': 10001,
                }
            else:
                response_data = {
                    'message': u'企业用户信息已完善',
                    'ret_code': 10000,
                }

                return HttpResponse(json.dumps(response_data), status=200, content_type='application/json')
        else:
            response_data = {
                'message': u'非企业用户',
                'ret_code': 20001,
            }

        return HttpResponse(json.dumps(response_data), status=400, content_type='application/json')
