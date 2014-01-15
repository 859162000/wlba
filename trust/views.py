from django.contrib.auth import get_user_model

from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

import logging
from wanglibao.urls import UserSerializer

logger = logging.getLogger(__name__)


#class UserSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = get_user_model()

@api_view(['POST'])
@permission_classes((AllowAny,))
def register(request):
    VALID_USER_FIELDS = [f.name for f in get_user_model()._meta.fields]
    DEFAULTS = {
        # you can define any defaults that you would like for the user, here
    }
    serialized = UserSerializer(data=request.DATA)
    if serialized.is_valid():
        user_data= {field: data for (field, data) in request.DATA.items() if field in VALID_USER_FIELDS}
        logger.info(user_data)
        user = get_user_model().objects.create_user(
            **user_data
        )
        return Response(UserSerializer(instance=user).data, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)
