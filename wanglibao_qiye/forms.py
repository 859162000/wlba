# encoding: utf-8

from django import forms
from .utils import detect_phone_for_identifier


class EnterpriseUserProfileForm(forms.Form):
    """企业用户认证资料验证表单"""

    company_name = forms.CharField(label="Company name", max_length=30, error_messages={'required': u'请输入公司名称'})
    certigier_name = forms.CharField(label="Certigier name", max_length=12, error_messages={'required': u'请输入授权人姓名'})
    certigier_phone = forms.IntegerField(label="Certigier phone", error_messages={'required': u'请输入授权人手机号'})
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

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name', '').strip()
        self.cleaned_data['company_name'] = company_name

        return self.cleaned_data

    def clean_certigier_name(self):
        certigier_name = self.cleaned_data.get('certigier_name', '').strip()
        self.cleaned_data['certigier_name'] = certigier_name

        return certigier_name

    def clean_phone(self):
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
        self.cleaned_data['company_address'] = company_address

        return self.cleaned_data

    def clean_company_account(self):
        company_account = self.cleaned_data.get('company_account', '').strip()
        self.cleaned_data['company_account'] = company_account

        return self.cleaned_data

    def clean_company_account_name(self):
        company_account_name = self.cleaned_data.get('company_account_name', '').strip()
        self.cleaned_data['company_account_name'] = company_account_name

        return self.cleaned_data

    def clean_deposit_bank_province(self):
        deposit_bank_province = self.cleaned_data.get('deposit_bank_province', '').strip()
        self.cleaned_data['deposit_bank_province'] = deposit_bank_province

        return self.cleaned_data

    def clean_deposit_bank_city(self):
        deposit_bank_city = self.cleaned_data.get('deposit_bank_city', '').strip()
        self.cleaned_data['deposit_bank_city'] = deposit_bank_city

        return self.cleaned_data

    def clean_bank_branch_address(self):
        bank_branch_address = self.cleaned_data.get('bank_branch_address', '').strip()
        self.cleaned_data['bank_branch_address'] = bank_branch_address

        return self.cleaned_data
