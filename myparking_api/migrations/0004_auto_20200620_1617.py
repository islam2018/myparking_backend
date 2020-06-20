# Generated by Django 2.2.9 on 2020-06-20 15:17

import datetime
from django.db import migrations, models
from django.utils.timezone import utc
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('myparking_api', '0003_auto_20200603_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='propositions',
            field=djongo.models.fields.ArrayReferenceField(on_delete=djongo.models.fields.ArrayReferenceField._on_delete, to='myparking_api.Porposition'),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='reservations',
            field=djongo.models.fields.ArrayReferenceField(on_delete=djongo.models.fields.ArrayReferenceField._on_delete, to='myparking_api.Reservation'),
        ),
        migrations.AlterField(
            model_name='message',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 20, 15, 17, 15, 173789, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateEntreeEffective',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 20, 16, 17, 15, 171790)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateEntreePrevue',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 20, 16, 17, 15, 171790)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateReservation',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 20, 16, 17, 15, 171790)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateSortieEffective',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 20, 16, 17, 15, 171790)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateSortiePrevue',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 20, 16, 17, 15, 171790)),
        ),
        migrations.AlterField(
            model_name='signalement',
            name='dateDebut',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 20, 15, 17, 15, 172789, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='signalement',
            name='dateFin',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 20, 15, 17, 15, 172789, tzinfo=utc)),
        ),
    ]
