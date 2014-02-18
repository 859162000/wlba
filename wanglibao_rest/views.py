import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.timezone import utc
import random
import requests
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.decorators import link
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from wanglibao_portfolio.models import UserPortfolio
from wanglibao_portfolio.serializers import PortfolioSerializer, UserPortfolioSerializer
from wanglibao_rest.serializers import UserSerializer
from wanglibao_profile.models import PhoneValidateCode


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


def generate_validate_code():
    return "%d" % (random.randrange(1000, 10000))


class PhoneValidateView(APIView):
    """
    The phone validate view which accept a post request and send a validate code to the phone
    """
    permission_classes = ()
    throttle_classes = (UserRateThrottle,)

    def post(self, request, phone, format=None):
        phone_number = phone
        phone_number = phone_number.strip()

        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        validate_code = generate_validate_code()

        try:
            phone_validate_code_item = PhoneValidateCode.objects.get(phone=phone_number)

            if (now - phone_validate_code_item.last_send_time) <= datetime.timedelta(minutes=1):
                # TODO find a proper status code
                return Response({
                    "error": "Called too frequently"
                }, status=400)
            else:
                phone_validate_code_item.validate_code = validate_code
                phone_validate_code_item.last_send_time = now
                phone_validate_code_item.save()

        except PhoneValidateCode.DoesNotExist:
            phone_validate_code_item = PhoneValidateCode.objects.create(
                phone=phone_number,
                validate_code=validate_code,
                last_send_time=now)
            phone_validate_code_item.save()

         # Send the validate message to mobile TODO Add throttling on ip, phone number
        content = render_to_string('activation-sms.html', {'validation_code': validate_code})
        params = {
            'account': settings.SMS_ACCOUNT,
            'password': settings.SMS_PASSWORD,
            'mobile': phone_number,
            'content': content
        }

        url = settings.SMS_URL
        r = requests.post(url, params)

        if r.status_code != 200:
            return Response({
                "error": "Failed to send sms"
            }, status=400)

        import xml.etree.ElementTree as ET
        doc = ET.fromstring(r.content)

        namespace = doc.tag.lstrip('{').split('}')[0].join(['{', '}'])
        return_code = int(next(doc.iter(namespace + 'code')).text)

        # TODO for errors log it out
        # TODO for all logs, when pii data embeded, wrap the code with special tag [type=value] [phone=18888888888]
        #      future mining can utilize this.

        if return_code != 2:
            return Response({
                "phone": phone_number,
                "message": "Failed to send sms"
            }, status=400)

        return Response({
            "phone": phone_number,
            "last_send_time": now
        })

class RegisterByPhone(APIView):
    """
    The register by phone view, which provide a form, generate a code and send it to the phone
    If the user submitted the code successfully, then create a user object and let him specify a
    password
    In case the code not received, user can resend it after 60 seconds
    """
    permission_classes = ()

    def post(self, request):
        phone_number = request.DATA["phone"]
        validate_code = request.DATA["validate_code"]

        now = datetime.datetime.utcnow().replace(tzinfo=utc)

        try:
            phone_validate_code_item = PhoneValidateCode.objects.get(phone=phone_number)
            if now - phone_validate_code_item.last_send_time > datetime.timedelta(minutes=20):
                return Response(
                    {
                        "message": "The validate code is send 20 minutes ago, recreate another one",
                        "data": request.DATA
                    },
                    status=400
                )
            if phone_validate_code_item.validate_code == validate_code:
                phone_validate_code_item.is_validated = True
                phone_validate_code_item.save()

                # Now create a new user for this phone
                new_user = User.objects.create(username="sj"+phone_number)
                new_user.set_password('randomNumber')

                #TODO bind profile with user
                #new_user.phone_number = phone_number
                new_user.save()
                user_serialized = UserSerializer(new_user)

                return Response({
                    "message": "The validate passed",
                    "data": user_serialized.data},
                    status=200
                )
            else:
                return Response(
                    {
                        "message": "The validate code is not correct",
                        "data": request.DATA
                    },
                    status=400)
        except PhoneValidateCode.DoesNotExist, e:
            return Response({
                "message": "Can't find related record for the phone",
                "data": request.DATA
            }, status=400)


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
