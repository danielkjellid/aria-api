# Generated by Django 3.2.11 on 2022-01-22 21:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audit_logs', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='logentry',
            options={'permissions': (('has_audit_logs_list', 'Can view audit logs'), ('has_audit_logs_edit', 'Can edit a single log instance'), ('has_audit_logs_delete', 'Can delete a single log instance')), 'verbose_name': 'Audit log entry', 'verbose_name_plural': 'Audit log entries'},
        ),
    ]