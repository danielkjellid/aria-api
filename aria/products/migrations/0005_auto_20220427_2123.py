# Generated by Django 3.2.12 on 2022-04-27 19:23

import aria.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_product_new_materials'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='product',
            managers=[
            ],
        ),
        migrations.RemoveField(
            model_name='product',
            name='applications',
        ),
        migrations.RemoveField(
            model_name='product',
            name='new_materials',
        ),
        migrations.RemoveField(
            model_name='product',
            name='styles',
        ),
        migrations.AlterField(
            model_name='color',
            name='color_hex',
            field=models.CharField(max_length=7, unique=True, verbose_name='color code'),
        ),
        migrations.AlterField(
            model_name='color',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='product',
            name='available_in_special_sizes',
            field=models.BooleanField(default=False, help_text='Designates whether the product comes in sizes out of the ordinary', verbose_name='available in special sizes'),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='product',
            name='materials',
            field=aria.core.fields.ChoiceArrayField(base_field=models.CharField(choices=[('kompositt', 'Kompositt'), ('dado kvarts', 'DADOkvarts'), ('rustfritt stål', 'Rustfritt stål'), ('pusset stål', 'Pusset stål'), ('metall', 'Metall'), ('tre', 'Tre'), ('laminat', 'Laminat'), ('glass', 'Glass'), ('marmor', 'Marmor')], max_length=50), help_text='Material product is made of. Want to add more options? Reach out to Daniel.', null=True, size=None),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=255, verbose_name='product name'),
        ),
        migrations.AlterField(
            model_name='product',
            name='new_description',
            field=models.TextField(verbose_name='new description'),
        ),
        migrations.AlterField(
            model_name='product',
            name='search_keywords',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='search keywords'),
        ),
        migrations.AlterField(
            model_name='product',
            name='short_description',
            field=models.TextField(help_text='The short description will be displayed on the top part of the product, above the variant selection', null=True, verbose_name='short description'),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(help_text='A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs.', max_length=255, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.IntegerField(choices=[(1, 'Draft'), (2, 'Hidden'), (3, 'Available'), (4, 'Discontinued')], default=1, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='product',
            name='unit',
            field=models.IntegerField(choices=[(1, 'm2'), (2, 'stk')], default=1, verbose_name='unit'),
        ),
        migrations.AlterField(
            model_name='product',
            name='vat_rate',
            field=models.FloatField(default=0.25, verbose_name='VAT rate'),
        ),
        migrations.AlterField(
            model_name='productfile',
            name='name',
            field=models.CharField(max_length=255, verbose_name='product file name'),
        ),
        migrations.AlterField(
            model_name='productoption',
            name='status',
            field=models.IntegerField(choices=[(1, 'Draft'), (2, 'Hidden'), (3, 'Available'), (4, 'Discontinued')], default=3, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='shape',
            name='name',
            field=models.CharField(max_length=30, unique=True, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='size',
            name='circumference',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Circumference in centimeters', max_digits=6, null=True, verbose_name='circumference'),
        ),
        migrations.AlterField(
            model_name='size',
            name='depth',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Depth in centimeters', max_digits=6, null=True, verbose_name='depth'),
        ),
        migrations.AlterField(
            model_name='size',
            name='height',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Height in centimeters', max_digits=6, null=True, verbose_name='height'),
        ),
        migrations.AlterField(
            model_name='size',
            name='width',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Width in centimeters', max_digits=6, null=True, verbose_name='width'),
        ),
        migrations.AlterField(
            model_name='variant',
            name='is_standard',
            field=models.BooleanField(default=False, help_text='Designates if a variant should be treated as standard. This is to avoid multiple instances of the same variant. This field will also prevent cleanup deletion of these models.', verbose_name='standard'),
        ),
        migrations.AlterField(
            model_name='variant',
            name='name',
            field=models.CharField(max_length=255, verbose_name='product variant name'),
        ),
    ]
