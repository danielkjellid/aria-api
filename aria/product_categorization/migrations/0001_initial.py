# Generated by Django 3.2.11 on 2022-01-21 12:44

import aria.core.utils
import django.contrib.sites.managers
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created time')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='modified time')),
                ('image', models.ImageField(blank=True, default='media/front/default_2048x1150.jpeg', upload_to=aria.core.utils.get_static_asset_upload_path, verbose_name='Image')),
                ('apply_filter', models.BooleanField(default=False, help_text='Apply filter to image if the image is light to maintain an acceptable contrast', verbose_name='Apply filter')),
                ('name', models.CharField(max_length=255, verbose_name='Category name')),
                ('slug', models.SlugField(help_text='A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs.', verbose_name='Slug')),
                ('ordering', models.PositiveSmallIntegerField(blank=True, default=0, help_text='Order  in which the category should be displayed.', verbose_name='Order')),
                ('width', models.CharField(blank=True, choices=[('full', 'Fullwidth'), ('half', 'Half')], default='full', max_length=4, null=True, verbose_name='Width')),
                ('display_in_navbar', models.BooleanField(default=True, help_text='Designates whether the category should be displayed in the nav dropdown.', verbose_name='Display in navigation bar')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether the category should be treated as active.', verbose_name='Active')),
                ('sites', models.ManyToManyField(blank=True, related_name='categories', to='sites.Site')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Category name')),
                ('slug', models.SlugField(help_text='A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs.', verbose_name='Slug')),
                ('ordering', models.PositiveSmallIntegerField(blank=True, default=0, help_text='Order  in which the category should be displayed.', verbose_name='Order')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether the category should be treated as active.', verbose_name='Active')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children', to='product_categorization.category')),
                ('sites', models.ManyToManyField(blank=True, related_name='subcategories', to='sites.Site')),
            ],
            options={
                'verbose_name': 'Subcategory',
                'verbose_name_plural': 'Subcategories',
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
    ]
