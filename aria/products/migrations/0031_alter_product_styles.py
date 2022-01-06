# Generated by Django 3.2.9 on 2022-01-06 13:37

import aria.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0030_alter_product_materials'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='styles',
            field=aria.core.fields.ChoiceArrayField(base_field=models.CharField(choices=[('classic', 'Klassisk'), ('concrete', 'Betong'), ('luxurious', 'Luksus'), ('marble', 'Marmor'), ('natural', 'Naturlig'), ('scandinavian', 'Skandinavisk'), ('structured', 'Strukturert'), ('woodenstructure', 'Trestruktur'), ('modern', 'Moderne'), ('circular', 'Rundt'), ('square', 'Firkantet'), ('oval', 'Ovalt'), ('mirrorwithlight', 'Speil med lys'), ('industrial', 'Industriell')], max_length=50), help_text='Which style the product line represent. Want to add more options? Reach out to Daniel.', null=True, size=None),
        ),
    ]
