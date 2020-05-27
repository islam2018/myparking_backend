# Generated by Django 2.2.9 on 2020-05-27 14:33

import datetime
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
                ('compte', models.TextField(default='app')),
                ('idCompte', models.TextField(default='null')),
                ('nom', models.TextField(default='')),
                ('numTel', models.TextField(default='')),
                ('prenom', models.TextField(default='')),
                ('position', djongo.models.fields.ListField()),
                ('auth', models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='driverProfile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Equipement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designation', models.TextField()),
                ('iconUrl', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Etage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('jour', models.IntegerField()),
                ('HeureOuverture', models.TimeField()),
                ('HeureFermeture', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='PaiementInstance',
            fields=[
                ('idPaimentInstance', models.AutoField(primary_key=True, serialize=False)),
                ('montant', models.TextField()),
                ('date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Paiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.TextField()),
                ('iconUrl', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Parking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nbEtages', models.IntegerField()),
                ('nbPlaces', models.IntegerField()),
                ('nbPlacesLibres', models.IntegerField()),
                ('nom', models.TextField()),
                ('adresse', models.TextField()),
                ('imageUrl', models.TextField()),
                ('lattitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('equipements', djongo.models.fields.ArrayReferenceField(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, to='myparking_api.Equipement')),
                ('etages', djongo.models.fields.ArrayReferenceField(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, to='myparking_api.Etage')),
                ('horaires', djongo.models.fields.ArrayReferenceField(blank=True, on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Horaire')),
                ('paiments', djongo.models.fields.ArrayReferenceField(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, to='myparking_api.Paiment')),
            ],
        ),
        migrations.CreateModel(
            name='Tarif',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duree', models.FloatField()),
                ('prix', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Terme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenu', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codeReservation', models.TextField(default='')),
                ('hashId', models.TextField()),
                ('qrUrl', models.TextField()),
                ('state', models.TextField(default='En cours')),
                ('etageAttribue', models.IntegerField(default=1)),
                ('placeAttribue', models.IntegerField(default=1)),
                ('dateReservation', models.DateTimeField(default=datetime.datetime(2020, 5, 27, 15, 32, 58, 359715))),
                ('dateEntreePrevue', models.DateTimeField(default=datetime.datetime(2020, 5, 27, 15, 32, 58, 359715))),
                ('dateSortiePrevue', models.DateTimeField(default=datetime.datetime(2020, 5, 27, 15, 32, 58, 359715))),
                ('dateEntreeEffective', models.DateTimeField(default=datetime.datetime(2020, 5, 27, 15, 32, 58, 359715))),
                ('dateSortieEffective', models.DateTimeField(default=datetime.datetime(2020, 5, 27, 15, 32, 58, 359715))),
                ('automobiliste', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Automobiliste')),
                ('paiementInstance', models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, to='myparking_api.PaiementInstance')),
                ('paiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Paiment')),
                ('parking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Parking')),
            ],
        ),
        migrations.CreateModel(
            name='Porposition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(default=0)),
                ('automobiliste', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Automobiliste')),
                ('parking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Parking')),
            ],
        ),
        migrations.AddField(
            model_name='parking',
            name='tarifs',
            field=djongo.models.fields.ArrayReferenceField(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, to='myparking_api.Tarif'),
        ),
        migrations.AddField(
            model_name='parking',
            name='termes',
            field=djongo.models.fields.ArrayReferenceField(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, to='myparking_api.Terme'),
        ),
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TextField()),
                ('centroid', djongo.models.fields.ListField()),
                ('drivers', djongo.models.fields.ArrayReferenceField(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Automobiliste')),
                ('parkings', djongo.models.fields.ArrayReferenceField(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Parking')),
                ('propositions', djongo.models.fields.ArrayReferenceField(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Porposition')),
                ('reservations', djongo.models.fields.ArrayReferenceField(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Reservation')),
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
                ('nom', models.TextField(default='')),
                ('prenom', models.TextField(default='')),
                ('auth', models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='agentProfile', to=settings.AUTH_USER_MODEL)),
                ('parking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Parking')),
            ],
        ),
    ]
