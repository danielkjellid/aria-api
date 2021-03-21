# Generated by Django 3.0.7 on 2021-03-20 14:13

import django.contrib.sites.managers
from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('inventory', '0037_auto_20210319_1928'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='category',
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='subcategory',
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AddField(
            model_name='category',
            name='sites',
            field=models.ManyToManyField(blank=True, related_name='category_site', to='sites.Site'),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='sites',
            field=models.ManyToManyField(blank=True, related_name='subcategory_site', to='sites.Site'),
        ),
    ]