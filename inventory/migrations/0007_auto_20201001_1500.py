# Generated by Django 3.0.7 on 2020-10-01 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_auto_20201001_1455'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productfile',
            old_name='upload',
            new_name='file',
        ),
        migrations.RemoveField(
            model_name='productfile',
            name='available_for_download',
        ),
    ]