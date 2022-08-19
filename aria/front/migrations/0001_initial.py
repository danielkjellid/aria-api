# Generated by Django 4.0.5 on 2022-06-27 19:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='OpeningHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Opening hours',
                'verbose_name_plural': 'Opening hours',
            },
        ),
        migrations.CreateModel(
            name='SiteMessageLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SiteMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created time')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='modified time')),
                ('text', models.TextField(help_text='Message body, can contain some html.')),
                ('message_type', models.CharField(choices=[('danger', 'Danger/error'), ('warning', 'Warning'), ('info', 'Info'), ('success', 'Success')], max_length=50)),
                ('show_message_at', models.DateTimeField(blank=True, help_text='When the message should be visible from. Leave empty to display the message immediately.', null=True, verbose_name='Show from')),
                ('show_message_to', models.DateTimeField(blank=True, help_text='When the message should disappear. Leave emtpy to display the message indefinitely', null=True, verbose_name='Show to')),
                ('locations', models.ManyToManyField(blank=True, help_text='Locations to show this particular site message. Leave empty to display message at a global level.', to='front.sitemessagelocation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OpeningHoursDeviationTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True)),
                ('site_message', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deviation_templates', to='front.sitemessage')),
            ],
        ),
        migrations.CreateModel(
            name='OpeningHoursDeviation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active_at', models.DateTimeField(verbose_name='Time when deviation is active from')),
                ('active_to', models.DateTimeField(verbose_name='Time when deviation is active to')),
                ('description', models.TextField(null=True)),
                ('disable_appointment_bookings', models.BooleanField(default=False)),
                ('opening_hours', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deviations', to='front.openinghours')),
                ('template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deviations', to='front.openinghoursdeviationtemplate')),
            ],
        ),
        migrations.CreateModel(
            name='OpeningHoursTimeSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.CharField(choices=[('monday', 'Mandag'), ('tuesday', 'Tirsdag'), ('wednesday', 'Onsdag'), ('thursday', 'Torsdag'), ('friday', 'Fredag'), ('saturday', 'Lørdag'), ('sunday', 'Søndag')], max_length=50)),
                ('opening_at', models.TimeField(blank=True, null=True, verbose_name='Opening time')),
                ('closing_at', models.TimeField(blank=True, null=True, verbose_name='Closing time')),
                ('is_closed', models.BooleanField(default=False, verbose_name='Is closed on this day')),
                ('opening_hours', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='time_slots', to='front.openinghours')),
                ('opening_hours_deviation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='time_slots', to='front.openinghoursdeviation')),
            ],
            options={
                'unique_together': {('opening_hours', 'weekday')},
            },
        ),
    ]
