# encoding:utf-8
import urlparse

from django.contrib.auth import get_user_model
from django.core.urlresolvers import resolve
from django.db.models import Q
from django.db.models import F
from django.http import QueryDict
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from wanglibao_account.utils import create_user
from wanglibao_portfolio.models import UserPortfolio
from wanglibao_portfolio.serializers import UserPortfolioSerializer
from wanglibao_rest.serializers import AuthTokenSerializer, RegisterUserSerializer
from wanglibao_sms.utils import send_validation_code
from wanglibao_sms.models import PhoneValidateCode
from wanglibao.const import ErrorNumber
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao_account.models import VerifyCounter
from wanglibao_account.utils import verify_id


class UserPortfolioView(generics.ListCreateAPIView):
    queryset = UserPortfolio.objects.all()
    serializer_class = UserPortfolioSerializer

    def get_queryset(self):
        user_pk = self.kwargs['user_pk']
        return self.queryset.filter(user_id=user_pk)


class SendValidationCodeView(APIView):
    """
    The phone validate view which accept a post request and send a validate code to the phone
    """
    permission_classes = ()
    throttle_classes = (UserRateThrottle,)

    def post(self, request, phone, format=None):
        phone_number = phone.strip()
        status, message = send_validation_code(phone_number)
        return Response({
                            'message': message
                        }, status=status)


class SendRegisterValidationCodeView(APIView):
    """
    The phone validate view which accept a post request and send a validate code to the phone
    """
    permission_classes = ()
    throttle_classes = (UserRateThrottle,)

    def post(self, request, phone, format=None):
        phone_number = phone.strip()
        phone_check = WanglibaoUserProfile.objects.filter(phone=phone_number, phone_verified=True)
        if phone_check:
            return Response({
                                "message": u"该手机号已经被注册，不能重复注册",
                                "error_number": ErrorNumber.duplicate
                            }, status=400)


        phone_validate_code_item = PhoneValidateCode.objects.filter(phone=phone_number).first()
        if phone_validate_code_item:
            count = phone_validate_code_item.code_send_count
            if count > 10:
                return Response({
                                "message": u"该手机号验证次数过于频繁，请联系客服人工注册",
                                "error_number": ErrorNumber.duplicate
                            }, status=400)

        status, message = send_validation_code(phone_number)
        return Response({
                        'message': message
                        }, status=status)


class RegisterAPIView(APIView):
    permission_classes = ()
    # throttle_classes = (UserRateThrottle,)
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            create_user(serializer.object['identifier'], serializer.object['password'], serializer.object['nickname'])
            return Response({'message': 'user generated'})
        return Response(serializer.errors, status=status.HTTP_200_OK)


class UserExisting(APIView):
    permission_classes = ()

    def get(self, request, identifier, format=None):
        """
        Get whether the user existing
        """

        query = Q(email=identifier) \
                | \
                (Q(wanglibaouserprofile__phone=identifier) &
                 Q(wanglibaouserprofile__phone_verified=True))

        try:
            get_user_model().objects.get(query)

            return Response({
                                "existing": True
                            }, status=200)
        except get_user_model().DoesNotExist:
            return Response({
                                "existing": False
                            }, status=200)


class IdValidate(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        name = request.DATA.get("name", "")
        id_number = request.DATA.get("id_number", "")

        verify_counter, created = VerifyCounter.objects.get_or_create(user=user)

        if verify_counter.count >= 3:
            return Response({
                                "message": u"验证次数超过三次，请联系客服进行人工验证 4008-588-066",
                                "error_number": ErrorNumber.try_too_many_times
                            }, status=400)


        id_verify_count = WanglibaoUserProfile.objects.filter(id_number=id_number).count()

        if id_verify_count >= 3:
            print 'id_verify_count', id_verify_count
            return Response({
                                "message": u"您的身份证已绑定了三个帐号，无法继续验证，请联系客服人工验证 4008-588-066",
                                "error_number": ErrorNumber.id_verify_times_error
                            }, status=400)


        verify_record, error = verify_id(name, id_number)

        verify_counter.count = F('count') + 1
        verify_counter.save()

        if error or not verify_record.is_valid:
            return Response({
                                "message": u"验证失败，拨打客服电话进行人工验证",
                                "error_number": ErrorNumber.unknown_error
                            }, status=400)

        user.wanglibaouserprofile.id_number = id_number
        user.wanglibaouserprofile.name = name
        user.wanglibaouserprofile.id_is_valid = True
        user.wanglibaouserprofile.save()

        return Response({
                            "validate": True
                        }, status=200)


class AdminIdValidate(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        phone = request.DATA.get("phone", "")
        name = request.DATA.get("name", "")
        id_number = request.DATA.get("id_number", "")

        verify_record, error = verify_id(name, id_number)

        if error:
            return Response({
                        "message": u"验证失败",
                        "error_number": ErrorNumber.unknown_error
                    }, status=400)

        user = get_user_model().objects.get(wanglibaouserprofile__phone=phone)
        user.wanglibaouserprofile.id_number = id_number
        user.wanglibaouserprofile.name = name
        user.wanglibaouserprofile.id_is_valid = True
        user.wanglibaouserprofile.save()

        return Response({
                            "validate": True
                        }, status=200)


class ObtainAuthTokenCustomized(ObtainAuthToken):
    serializer_class = AuthTokenSerializer


obtain_auth_token = ObtainAuthTokenCustomized.as_view()
