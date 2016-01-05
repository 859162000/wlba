# encoding: utf-8

from django import forms
from .utils import detect_phone_for_identifier
from wanglibao_sms.utils import validate_validation_code
from .models import EnterpriseUserProfile


class EnterpriseUserProfileForm(forms.Form):
    """企业用户认证资料验证表单"""

    company_name = forms.CharField(label="Company name", max_length=30, error_messages={'required': u'请输入公司名称'})
    business_license = forms.CharField(label="Business license", max_length=255,
                                       error_messages={'required': u'请选择营业执照'})
    registration_cert = forms.CharField(label="Registration cert", max_length=255,
                                        error_messages={'required': u'请选择税务登记证'})
    certigier_name = forms.CharField(label="Certigier name", max_length=12, error_messages={'required': u'请输入授权人姓名'})
    certigier_phone = forms.CharField(label="Certigier phone", error_messages={'required': u'请输入授权人手机号'})
    company_address = forms.CharField(label="Company address", max_length=255,
                                      error_messages={'required': u'请输入公司地址'})
    company_account = forms.CharField(label="Company account", max_length=64,
                                      error_messages={'required': u'请输入公司账户账号'})
    company_account_name = forms.CharField(label="Company account name", max_length=30,
                                           error_messages={'required': u'请输入公司账户名称'})
    deposit_bank_province = forms.CharField(label="Deposit bank province", max_length=10,
                                            error_messages={'required': u'请输入公司开户行所在省份'})
    deposit_bank_city = forms.CharField(label="Deposit bank city", max_length=10,
                                        error_messages={'required': u'请输入公司开户行所在市县'})
    bank_branch_address = forms.CharField(label="Bank branch address", max_length=100,
                                          error_messages={'required': u'请输入开户行支行所在地'})
    trade_pwd = forms.CharField(label="Trade pwd", max_length=50, error_messages={'required': u'请输入交易密码'})
    validate_code = forms.CharField(label="Validate code for phone", error_messages={'required': u'请输入短信验证码'})
    bank = forms.CharField(label="Bank", error_messages={'required': u'请输入所属银行'})

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name', '').strip()

        return company_name

    def clean_business_license(self):
        business_license = self.cleaned_data.get('business_license', '').strip()

        return business_license

    def clean_registration_cert(self):
        registration_cert = self.cleaned_data.get('registration_cert', '').strip()

        return registration_cert

    def clean_certigier_name(self):
        certigier_name = self.cleaned_data.get('certigier_name', '').strip()

        return certigier_name

    def clean_certigier_phone(self):
        certigier_phone = self.cleaned_data.get('certigier_phone', '').strip()
        if not detect_phone_for_identifier(certigier_phone):
            raise forms.ValidationError(
                message='invalid phone number',
                code="10001",
            )

        self.cleaned_data['certigier_phone'] = certigier_phone

        return self.cleaned_data

    def clean_company_address(self):
        company_address = self.cleaned_data.get('company_address', '').strip()

        return company_address

    def clean_company_account(self):
        company_account = self.cleaned_data.get('company_account', '').strip()

        return company_account

    def clean_company_account_name(self):
        company_account_name = self.cleaned_data.get('company_account_name', '').strip()

        return company_account_name

    def clean_deposit_bank_province(self):
        deposit_bank_province = self.cleaned_data.get('deposit_bank_province', '').strip()

        return deposit_bank_province

    def clean_deposit_bank_city(self):
        deposit_bank_city = self.cleaned_data.get('deposit_bank_city', '').strip()

        return deposit_bank_city

    def clean_bank_branch_address(self):
        bank_branch_address = self.cleaned_data.get('bank_branch_address', '').strip()

        return bank_branch_address

    def clean_trade_pwd(self):
        trade_pwd = self.cleaned_data.get('trade_pwd', '').strip()

        return trade_pwd

    def clean_validate_code(self):
        if 'certigier_phone' in self.cleaned_data:
            certigier_phone = self.cleaned_data["certigier_phone"].strip()
            if detect_phone_for_identifier(certigier_phone):
                validate_code = self.cleaned_data.get('validate_code', '')
                if validate_code:
                    status, message = validate_validation_code(certigier_phone, validate_code)
                    if status != 200:
                        raise forms.ValidationError(
                            # Modify by hb on 2015-12-02
                            # self.error_messages['validate code not match'],
                            message,
                            code='validate_code_error',
                        )
                else:
                    raise forms.ValidationError(
                        self.error_messages['validate must not be null'],
                        code='10002',
                    )

        return self.cleaned_data

    def clean_bank(self):
        bank = self.cleaned_data.get('bank', '').strip()
        if bank not in [i for i, j in EnterpriseUserProfile.BANK]:
            raise forms.ValidationError(
                u'无效所属银行',
                code='10003',
            )

        return bank
