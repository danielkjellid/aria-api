# Generated by Django 4.0.5 on 2022-07-08 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='disabled_emails',
            field=models.BooleanField(default=False, help_text='Decides if a user receives email from us. Typically used if we do not want a user to receive marketing (competitors).'),
        ),
    ]