# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework.serializers import HyperlinkedModelSerializer
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from marketing.models import PromotionToken
from wanglibao_account.utils import detect_identifier_type
from wanglibao_sms.utils import validate_validation_code


class AuthTokenSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')

        if identifier and password:
            user = authenticate(identifier=identifier, password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError('Unable to login with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "identifier" and "password"')


class RegisterUserSerializer(serializers.Serializer):
    """
    This serializer is used to do validation on the register api endpoint
    """
    identifier = serializers.CharField()
    password = serializers.CharField()
    nickname = serializers.CharField()
    validate_code = serializers.CharField()
   # invite_code = serializers.CharField()

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')
        validate_code = attrs.get('validate_code')
        nickname = attrs.get('nickname')

        if identifier and password and validate_code and nickname:
            identifier_type = detect_identifier_type(identifier)

            if identifier_type != 'phone':
                raise serializers.ValidationError(u"手机号输入错误")
            else:
                status, message = validate_validation_code(identifier, validate_code)
                if status != 200:
                    raise serializers.ValidationError(u"验证码输入错误")

                if User.objects.filter(wanglibaouserprofile__phone=identifier, wanglibaouserprofile__phone_verified=True).exists():
                    raise serializers.ValidationError(u"该手机号已经注册")
            return super(RegisterUserSerializer, self).validate(attrs)

        else:
            raise serializers.ValidationError(u"信息输入不完整")
