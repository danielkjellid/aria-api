# Generated by Django 3.2.11 on 2022-01-24 11:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audit_logs', '0002_alter_logentry_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='logentry',
            old_name='user',
            new_name='author',
        ),
    ]
