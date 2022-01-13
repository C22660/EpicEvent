# Generated by Django 4.0.1 on 2022-01-10 17:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_alter_contracts_client_alter_events_client'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contracts',
            name='event',
        ),
        migrations.AddField(
            model_name='events',
            name='contract',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='AttachedContract', to='crm.contracts'),
        ),
    ]
