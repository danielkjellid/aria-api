# Generated by Django 4.0.5 on 2022-06-14 14:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0005_alter_openinghourstimeslot_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='openinghoursdeviation',
            name='time_slot',
        ),
    ]
