# Generated by Django 4.0.5 on 2022-06-14 14:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0004_alter_openinghourstimeslot_weekday'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='openinghourstimeslot',
            unique_together={('opening_hours', 'weekday')},
        ),
    ]
