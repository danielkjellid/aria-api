# Generated by Django 3.2.9 on 2021-11-25 20:10

import aria.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_auto_20211121_0023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='styles',
            field=aria.core.fields.ChoiceArrayField(base_field=models.CharField(choices=[('classic', 'Klassisk'), ('concrete', 'Betong'), ('luxurious', 'Luksus'), ('marble', 'Marmor'), ('natural', 'Naturlig'), ('scandinavian', 'Skandinavisk'), ('structured', 'Strukturert'), ('woodenstructure', 'Trestruktur'), ('modern', 'Moderne'), ('circular', 'Rundt'), ('square', 'Firkantet'), ('mirrorwithlight', 'Speil med lys')], max_length=50), help_text='Which style the product line represent. Want to add more options? Reach out to Daniel.', null=True, size=None),
        ),
    ]
