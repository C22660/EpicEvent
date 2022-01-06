# Generated by Django 4.0.1 on 2022-01-05 16:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Clients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=25, verbose_name='Prénom')),
                ('last_name', models.CharField(max_length=25, verbose_name='Nom')),
                ('email', models.CharField(max_length=100, verbose_name='Email')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Téléphone')),
                ('mobile', models.CharField(max_length=20, verbose_name='Mobile')),
                ('compagny_name', models.CharField(max_length=250, unique=True, verbose_name='Mobile')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('sales_contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Client',
                'ordering': ['compagny_name'],
            },
        ),
        migrations.CreateModel(
            name='Events',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('event_status', models.BooleanField(default=False, verbose_name='Réalisé')),
                ('attendees', models.IntegerField(blank=True, verbose_name='Participants')),
                ('event_date', models.DateField(blank=True, null=True)),
                ('note', models.TextField(blank=True, verbose_name='Commentaires')),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Clientevents', to='crm.clients')),
                ('suport_contact', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Support', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Contracts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('status', models.BooleanField(default=False, verbose_name='Signé')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, verbose_name='Montant')),
                ('payment_due', models.DateField(blank=True, null=True)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Clientcontracts', to='crm.clients')),
                ('sales_contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
