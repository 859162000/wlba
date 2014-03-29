from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.decorators import link
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from wanglibao_portfolio.models import UserPortfolio
from wanglibao_portfolio.serializers import PortfolioSerializer, UserPortfolioSerializer
from wanglibao_rest.serializers import UserSerializer
from wanglibao_sms.utils import send_validation_code


class UserViewSet(viewsets.ModelViewSet):
    model = User
    serializer_class = UserSerializer

    @link()
    def portfolio(self, request, *args, **kwargs):
        user = self.get_object()
        return Response(PortfolioSerializer(user.userportfolio.portfolio.all()[0]).data)


class UserPortfolioView(generics.ListCreateAPIView):
    queryset = UserPortfolio.objects.all()
    serializer_class = UserPortfolioSerializer

    def get_queryset(self):
        user_pk = self.kwargs['user_pk']
        return self.queryset.filter(user_id = user_pk)


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


class UserExisting(APIView):

    permission_classes = ()

    def get(self, request, format=None):
        """
        Get whether the user existing
        """
        username = request.GET['username']
        user_existing = User.objects.filter(username=username).count() > 0
        return Response({
            "existing": user_existing
        }, status=200)
