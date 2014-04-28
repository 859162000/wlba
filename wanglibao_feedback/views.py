from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from wanglibao.PaginatedModelViewSet import PaginatedModelViewSet
from wanglibao.permissions import AllowAnyPostOnlyAdminList
from wanglibao_feedback.models import Feedback
from wanglibao_feedback.serializers import FeedbackSerializer


class FeedbackViewSet(PaginatedModelViewSet):
    serializer_class = FeedbackSerializer
    model = Feedback
    throttle_classes = UserRateThrottle,
    permission_classes = AllowAnyPostOnlyAdminList,

    @property
    def allowed_methods(self):
        return 'GET', 'POST'

    def create(self, request):
        serializer = self.get_serializer(data=request.DATA)

        if serializer.is_valid():
            user = None
            if request.user and request.user.is_authenticated():
                user = request.user

            serializer.object.created_by = user
            serializer.object.save()
            return Response(serializer.data)
        else:
            return Response({
                'message': 'failed'
            }, status=400)
