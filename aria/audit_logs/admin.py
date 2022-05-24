from django.contrib import admin

from aria.audit_logs.models import LogEntry


class LogEntryAdmin(admin.ModelAdmin):
    list_display = [
        "author",
        "content_type",
        "object_id",
        "content_object",
        "change",
        "created_at",
    ]


admin.site.register(LogEntry, LogEntryAdmin)
