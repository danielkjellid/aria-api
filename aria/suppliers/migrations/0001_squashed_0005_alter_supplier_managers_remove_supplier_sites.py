# Generated by Django 4.0.6 on 2022-08-19 12:26

import datetime

import django.db.models.manager
from django.db import migrations, models
from django.utils.timezone import utc

import django_countries.fields

import aria.core.utils


class Migration(migrations.Migration):

    replaces = [('suppliers', '0001_initial'), ('suppliers', '0002_auto_20220225_2213'), ('suppliers', '0003_alter_supplier_image'), ('suppliers', '0004_alter_supplier_origin_country'), ('suppliers', '0005_alter_supplier_managers_remove_supplier_sites')]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Supplier name')),
                ('contact_first_name', models.CharField(max_length=255, verbose_name='Contact first name')),
                ('contact_last_name', models.CharField(max_length=255, verbose_name='Contact last name')),
                ('contact_email', models.EmailField(max_length=254, verbose_name='Contact email address')),
                ('supplier_discount', models.FloatField(blank=True, help_text='Supplier discount in percent. E.g. 0.2 = 20%', null=True)),
                ('origin_country', django_countries.fields.CountryField(max_length=2)),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether the category should be treated as active.', verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, default=datetime.datetime(2022, 2, 25, 21, 13, 19, 459286, tzinfo=utc), verbose_name='created time')),
                ('image', models.ImageField(blank=True, upload_to=aria.core.utils.get_static_asset_upload_path, verbose_name='Image')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='modified time')),
                ('website_link', models.CharField(default='https://example.com', max_length=255)),
            ],
            options={
                'verbose_name': 'supplier',
                'verbose_name_plural': 'suppliers',
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='supplier',
            managers=[
            ],
        ),
    ]
