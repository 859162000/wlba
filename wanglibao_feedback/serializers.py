from django.utils import timezone
from rest_framework import serializers
from wanglibao_feedback.models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(default=timezone.now, read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Feedback
