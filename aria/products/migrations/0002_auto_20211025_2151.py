# Generated by Django 3.0.7 on 2021-10-25 19:51

import aria.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_imported_from_external_source',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='temp_applications',
            field=aria.core.fields.ChoiceArrayField(base_field=models.CharField(choices=[('ceiling', 'Tak'), ('floor', 'Gulv'), ('table', 'Bord'), ('outdoors', 'Utendørs'), ('sink', 'Vask'), ('walls', 'Vegger')], max_length=50), null=True, size=None),
        ),
        migrations.AddField(
            model_name='product',
            name='temp_materials',
            field=aria.core.fields.ChoiceArrayField(base_field=models.CharField(choices=[('ceramic', 'Keramikk'), ('metal', 'Metall'), ('porcelain', 'Porselen'), ('wood', 'Tre')], max_length=50), null=True, size=None),
        ),
        migrations.AddField(
            model_name='product',
            name='temp_styles',
            field=aria.core.fields.ChoiceArrayField(base_field=models.CharField(choices=[('classic', 'Klassisk'), ('concrete', 'Betong'), ('luxurious', 'Luksus'), ('marble', 'Marmor'), ('natural', 'Naturlig'), ('scandinavian', 'Skandinavisk'), ('structured', 'Strukturert')], max_length=50), null=True, size=None),
        ),
    ]