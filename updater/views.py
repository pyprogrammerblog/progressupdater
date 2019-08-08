from rest_framework import viewsets, mixins
from updater.serializers import LogUpdaterSerializer
from updater.models import LogUpdater

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class LogUpdaterModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Operations on Entries
    """
    queryset = LogUpdater.objects.all()
    serializer_class = LogUpdaterSerializer
    permission_classes = [IsAuthenticated, ]
