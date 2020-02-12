# Generated by Django 2.2.9 on 2020-02-11 14:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import djongo.models.fields
import myparking_api.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Automobiliste',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idAutomobiliste', models.IntegerField()),
                ('nom', models.TextField(default='')),
                ('prenom', models.TextField(default='')),
                ('auth', models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='driverProfile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Equipement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idEquipement', models.IntegerField()),
                ('designation', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Etage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idEtage', models.IntegerField()),
                ('nbPlaces', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idEvaluation', models.IntegerField()),
                ('note', models.IntegerField()),
                ('automobiliste', djongo.models.fields.EmbeddedField(model_container=myparking_api.models.Automobiliste, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Horaire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idHoraire', models.IntegerField()),
                ('HeureOuverture', models.TimeField()),
                ('HeureFermeture', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Paiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Parking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idParking', models.IntegerField()),
                ('nbEtages', models.IntegerField()),
                ('nbPlaces', models.IntegerField()),
                ('nom', models.TextField()),
                ('adresse', models.TextField()),
                ('imageUrl', models.TextField()),
                ('lattitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('horaire', djongo.models.fields.EmbeddedField(model_container=myparking_api.models.Horaire, null=True)),
                ('etages', djongo.models.fields.ArrayField(model_container=myparking_api.models.Etage)),
                ('tarifs', djongo.models.fields.ArrayField(model_container=myparking_api.models.Tarif)),
                ('equipements', djongo.models.fields.ArrayField(model_container=myparking_api.models.Equipement)),
            ],
        ),
        migrations.CreateModel(
            name='Tarif',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idTarif', models.IntegerField()),
                ('duree', models.FloatField()),
                ('prix', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idReservation', models.IntegerField()),
                ('date', models.DateField()),
                ('entreePrevue', models.DateField(default='something')),
                ('sortiePrevue', models.DateField()),
                ('entreeEffective', models.DateField()),
                ('sortieEffective', models.DateField()),
                ('automobiliste', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Automobiliste')),
                ('paiement', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Paiment')),
                ('parking', models.OneToOneField(default='something', on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Parking')),
            ],
        ),
        migrations.AddField(
            model_name='automobiliste',
            name='favoris',
            field=djongo.models.fields.ArrayReferenceField(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, to='myparking_api.Parking'),
        ),
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idAgent', models.IntegerField()),
                ('nom', models.TextField(default='')),
                ('prenom', models.TextField(default='')),
                ('parking', models.TextField()),
                ('auth', models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='agentProfile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]