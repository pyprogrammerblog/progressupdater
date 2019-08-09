import django_filters
from updater.models import LogUpdater


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = LogUpdater
        fields = ('task_name', 'task_uuid', 'status', 'finished')
