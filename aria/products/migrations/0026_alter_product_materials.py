# Generated by Django 3.2.9 on 2021-12-17 13:58

import aria.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0025_alter_product_materials'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='materials',
            field=aria.core.fields.ChoiceArrayField(base_field=models.CharField(choices=[('ceramic', 'Keramikk'), ('metal', 'Metall'), ('porcelain', 'Porselen'), ('wood', 'Tre'), ('oak', 'Eik'), ('mdf', 'MDF'), ('mirror', 'Speil'), ('brushedsteel', 'Pusset stål'), ('stainlesssteel', 'Rustfritt stål'), ('composite', 'Kompositt')], max_length=50), help_text='Material product is made of. Want to add more options? Reach out to Daniel.', null=True, size=None),
        ),
    ]