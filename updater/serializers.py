from updater.models import LogUpdater
from rest_framework import serializers


class LogUpdaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogUpdater
        fields = [
            'task_name',
            'task_uuid',
            'start',
            'end',
            'log',
            'exception',
            'finished',
            'status',
        ]
