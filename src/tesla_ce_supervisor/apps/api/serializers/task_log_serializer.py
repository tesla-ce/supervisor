"""Task serialize module."""
from rest_framework import serializers

from tesla_ce_supervisor.apps.api.models import TaskLog


class TaskLogSerializer(serializers.ModelSerializer):
    """TaskLog serialize model module."""
    class Meta:
        model = TaskLog
        fields = "__all__"
