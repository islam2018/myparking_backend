# Generated by Django 2.2.9 on 2020-04-18 19:24

import datetime
from django.db import migrations, models
import django.db.models.deletion
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('myparking_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='dateEntreeEffective',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 18, 20, 24, 2, 628534)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateEntreePrevue',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 18, 20, 24, 2, 627534)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateSortieEffective',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 18, 20, 24, 2, 628534)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateSortiePrevue',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 18, 20, 24, 2, 627534)),
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
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TextField()),
                ('drivers', djongo.models.fields.ArrayReferenceField(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Automobiliste')),
                ('parkings', djongo.models.fields.ArrayReferenceField(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Parking')),
                ('propositions', djongo.models.fields.ArrayReferenceField(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Porposition')),
            ],
        ),
    ]
