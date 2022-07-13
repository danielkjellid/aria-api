# Generated by Django 4.0.5 on 2022-07-08 16:48

import aria.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_auto_20220507_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='materials',
            field=aria.core.fields.ChoiceArrayField(base_field=models.CharField(choices=[('kompositt', 'Kompositt'), ('dado kvarts', 'DADOkvarts'), ('rustfritt stål', 'Rustfritt stål'), ('pusset stål', 'Pusset stål'), ('metall', 'Metall'), ('tre', 'Tre'), ('laminat', 'Laminat'), ('glass', 'Glass'), ('marmor', 'Marmor')], max_length=50), help_text=('Material product is made of. Want to add more options? Reach out to Daniel.',), null=True, size=None),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(help_text=('A slug is a short label for something, containing only letters, numbers, underscores or hyphens. They’re generally used in URLs.',), max_length=255, verbose_name='slug'),
        ),
    ]