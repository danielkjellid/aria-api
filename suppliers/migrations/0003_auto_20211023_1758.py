# Generated by Django 3.0.7 on 2021-10-23 15:58

import django.contrib.sites.managers
from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('suppliers', '0002_auto_20211023_1758'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='supplier',
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AddField(
            model_name='supplier',
            name='sites',
            field=models.ManyToManyField(blank=True, related_name='suppliers', to='sites.Site'),
        ),
    ]
