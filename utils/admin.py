from django.contrib import admin

from utils.models import Note

class NoteAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'content_type',
        'object_id',
        'content_object',
        'note',
        'created_at'
    ]

admin.site.register(Note, NoteAdmin)


  
