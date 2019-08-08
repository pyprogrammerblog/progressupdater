# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import LogUpdater
from import_export.admin import ExportActionModelAdmin


@admin.register(LogUpdater)
class RoleAdmin(ExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('task_name', 'task_uuid', 'status', 'finished')
    search_fields = ('task_name', 'task_uuid', 'status')
    list_filter = ('task_name', 'task_uuid', 'status', 'finished')
