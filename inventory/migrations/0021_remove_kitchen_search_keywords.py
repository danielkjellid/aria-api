# Generated by Django 3.0.7 on 2020-10-28 23:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0020_auto_20201028_2346'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kitchen',
            name='search_keywords',
        ),
    ]
