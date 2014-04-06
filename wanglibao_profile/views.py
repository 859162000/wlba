from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from wanglibao_profile.serializers import ProfileSerializer


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Retrieve the current user's profile
        """
        user = request.user
        serializer = ProfileSerializer(user.wanglibaouserprofile)
        return Response(serializer.data)

    def put(self, request):
        """
        Update current user's profile
        """
        user = request.user
        profile_serializer = ProfileSerializer(user.wanglibaouserprofile)
        profile_serializer.from_native(request.DATA, None)
        profile_serializer.save()

        return Response(profile_serializer.data)
