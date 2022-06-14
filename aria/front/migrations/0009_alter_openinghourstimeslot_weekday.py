# Generated by Django 4.0.5 on 2022-06-14 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0008_rename_close_at_openinghourstimeslot_closing_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openinghourstimeslot',
            name='weekday',
            field=models.CharField(choices=[('monday', 'Mandag'), ('tuesday', 'Tirsdag'), ('wednesday', 'Onsdag'), ('thursday', 'Torsdag'), ('friday', 'Fredag'), ('saturday', 'Lørdag'), ('sunday', 'Søndag')], max_length=50),
        ),
    ]
