# Generated by Django 2.2.9 on 2020-05-28 15:39

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('myparking_api', '0012_auto_20200526_1334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='dateEntreeEffective',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 28, 16, 38, 50, 581739)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateEntreePrevue',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 28, 16, 38, 50, 581241)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateReservation',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 28, 16, 38, 50, 581241)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateSortieEffective',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 28, 16, 38, 50, 581739)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateSortiePrevue',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 28, 16, 38, 50, 581739)),
        ),
        migrations.AlterField(
            model_name='signalement',
            name='dateDebut',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 28, 15, 38, 50, 582736, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='signalement',
            name='dateFin',
            field=models.DateTimeField(default=datetime.datetime(2020, 5, 28, 15, 38, 50, 582736, tzinfo=utc)),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('objet', models.TextField()),
                ('message', models.TextField()),
                ('date', models.DateTimeField(default=datetime.datetime(2020, 5, 28, 15, 38, 50, 583735, tzinfo=utc))),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Automobiliste')),
            ],
        ),
    ]