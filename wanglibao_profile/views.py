from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import View


class registerByPhone(View):
    """
    The register by phone view, which provide a form, generate a code and send it to the phone
    If the user submitted the code successfully, then create a user object and let him specify a
    password
    In case the code not received, user can resend it after 60 seconds
    """
    def post(self, request):
        return HttpResponse("Hello !!")



