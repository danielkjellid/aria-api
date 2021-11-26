from django.contrib import admin

from aria.notes.models import NoteEntry


class NoteEntryAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "content_type",
        "object_id",
        "content_object",
        "note",
        "created_at",
    ]


admin.site.register(NoteEntry, NoteEntryAdmin)
