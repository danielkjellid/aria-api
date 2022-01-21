# Generated by Django 3.2.11 on 2022-01-21 12:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NoteEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('note', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='updated at')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notes', to='contenttypes.contenttype', verbose_name='content type')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='note_entries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Note',
                'verbose_name_plural': 'Notes',
                'permissions': (('has_notes_add', 'Can add new notes'), ('has_note_edit', 'Can edit a single note instance'), ('has_note_delete', 'Can delete a single note instance')),
            },
        ),
    ]
