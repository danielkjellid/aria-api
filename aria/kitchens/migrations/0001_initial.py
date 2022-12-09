# Generated by Django 3.2.11 on 2022-01-21 12:44

import django.db.models.deletion
from django.db import migrations, models

import imagekit.models.fields

import aria.files.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('suppliers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Decor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('thumbnail', imagekit.models.fields.ProcessedImageField(blank=True, default='media/front/default_380x575.jpeg', help_text='Image must be above 380x575px', upload_to=aria.files.utils.asset_get_static_upload_path)),
                ('image', imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='t')),
                ('name', models.CharField(max_length=255, verbose_name='Kitchen decor name')),
            ],
            options={
                'verbose_name': 'Decor',
                'verbose_name_plural': 'Decors',
            },
        ),
        migrations.CreateModel(
            name='ExclusiveColor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Kitchen exclusive name')),
                ('color_hex', models.CharField(max_length=7, unique=True, verbose_name='Color code')),
            ],
            options={
                'verbose_name': 'Exclusive color',
                'verbose_name_plural': 'Exclusive colors',
            },
        ),
        migrations.CreateModel(
            name='LaminateColor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Kitchen laminate name')),
                ('color_hex', models.CharField(max_length=7, unique=True, verbose_name='Color code')),
            ],
            options={
                'verbose_name': 'Laminate color',
                'verbose_name_plural': 'Laminates colors',
            },
        ),
        migrations.CreateModel(
            name='Plywood',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('thumbnail', imagekit.models.fields.ProcessedImageField(blank=True, default='media/front/default_380x575.jpeg', help_text='Image must be above 380x575px', upload_to=aria.files.utils.asset_get_static_upload_path)),
                ('image', imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to='t')),
                ('name', models.CharField(max_length=255, verbose_name='Kitchen playwood name')),
            ],
            options={
                'verbose_name': 'Plywood',
                'verbose_name_plural': 'Plywoods',
            },
        ),
        migrations.CreateModel(
            name='SilkColor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Kitchen silk name')),
                ('color_hex', models.CharField(max_length=7, unique=True, verbose_name='Color code')),
            ],
            options={
                'verbose_name': 'Silk color',
                'verbose_name_plural': 'Silk colors',
            },
        ),
        migrations.CreateModel(
            name='TrendColor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Kitchen trend name')),
                ('color_hex', models.CharField(max_length=7, unique=True, verbose_name='Color code')),
            ],
            options={
                'verbose_name': 'Trend color',
                'verbose_name_plural': 'Trend colors',
            },
        ),
        migrations.CreateModel(
            name='Kitchen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, default='media/front/default_2048x1150.jpeg', upload_to=aria.files.utils.asset_get_static_upload_path, verbose_name='Image')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Kitchen name')),
                ('status', models.IntegerField(choices=[(1, 'Draft'), (2, 'Hidden'), (3, 'Available'), (4, 'Discontinued')], default=1, verbose_name='Status')),
                ('slug', models.SlugField(help_text='A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs.', max_length=255, verbose_name='Slug')),
                ('thumbnail_description', models.CharField(max_length=255, verbose_name='Thumbnail description')),
                ('description', models.TextField(verbose_name='Description')),
                ('extra_description', models.TextField(blank=True, help_text='Will be displayed bellow pricing example', null=True, verbose_name='Extra description')),
                ('example_from_price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('can_be_painted', models.BooleanField(default=False, help_text='Designates whether the product can be painted in suppliers 2000 colors', verbose_name='Can be painted')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('apply_filter', models.BooleanField(default=False, help_text='Apply filter to image if the image is light to maintain an acceptable contrast', verbose_name='Apply filter')),
                ('decor_variants', models.ManyToManyField(blank=True, related_name='kitchen_decor', to='kitchens.Decor')),
                ('exclusive_variants', models.ManyToManyField(blank=True, related_name='kitchen_exclusive', to='kitchens.ExclusiveColor')),
                ('laminate_variants', models.ManyToManyField(blank=True, related_name='kitchen_decor', to='kitchens.LaminateColor')),
                ('plywood_variants', models.ManyToManyField(blank=True, related_name='kitchen_plywood', to='kitchens.Plywood')),
                ('silk_variants', models.ManyToManyField(blank=True, related_name='kitchen_silk', to='kitchens.SilkColor')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplier', to='suppliers.supplier')),
                ('trend_variants', models.ManyToManyField(blank=True, related_name='kitchen_decor', to='kitchens.TrendColor')),
            ],
            options={
                'verbose_name': 'Kitchen',
                'verbose_name_plural': 'Kitchens',
            },
        ),
    ]
