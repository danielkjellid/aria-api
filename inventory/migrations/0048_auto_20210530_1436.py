# Generated by Django 3.0.7 on 2021-05-30 12:36

import django.contrib.sites.managers
from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0047_auto_20210530_1420'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='productsitestate',
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
    ]