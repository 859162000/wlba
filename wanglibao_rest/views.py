# encoding:utf-8
import urlparse

from django.contrib.auth import get_user_model
from django.core.urlresolvers import resolve
from django.db.models import Q
from django.http import QueryDict
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from wanglibao_account.utils import create_user
from wanglibao_portfolio.models import UserPortfolio
from wanglibao_portfolio.serializers import UserPortfolioSerializer
from wanglibao_rest.serializers import AuthTokenSerializer, RegisterUserSerializer
from wanglibao_sms.utils import send_validation_code


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


class RegisterAPIView(APIView):
    permission_classes = ()
    # throttle_classes = (UserRateThrottle,)
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            create_user(serializer.object['identifier'], serializer.object['password'], serializer.object['nickname'])
            return Response({'message': 'user generated'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
                            }, status=404)


class ObtainAuthTokenCustomized(ObtainAuthToken):
    serializer_class = AuthTokenSerializer


obtain_auth_token = ObtainAuthTokenCustomized.as_view()


# REST Wrapper is a wrapper api which gets a list of api calls and return their result in one request
class RestWrapper(APIView):
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        query_params = request.QUERY_PARAMS
        urls = query_params.get('urls').split(',')
        if urls is None:
            return Response(status=status.HTTP_200_OK)

        results = []
        store_query_params = request.QUERY_PARAMS
        for url in urls:
            parse_result = urlparse.urlparse(url)
            if parse_result.netloc == '':
                r = resolve(parse_result.path)

                if issubclass(r.func.cls, APIView):
                    url_query_params = QueryDict(parse_result.query)
                    request._request.GET = url_query_params
                    response = r.func(request)
                    results.append({
                        'url': url,
                        'status_code': response.status_code,
                        'result': response.data
                    })

        request._request.GET = store_query_params

        return Response({
            'results': results,
        })
