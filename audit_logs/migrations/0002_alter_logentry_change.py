# Generated by Django 3.2.9 on 2021-11-25 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit_logs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logentry',
            name='change',
            field=models.JSONField(),
        ),
    ]
