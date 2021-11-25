from django.contrib import admin
from aria.audit_logs.models import LogEntry

class LogEntryAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'content_type',
        'object_id',
        'content_object',
        'change',
        'date_of_change'
    ]

admin.site.register(LogEntry, LogEntryAdmin)
