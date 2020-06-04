# Generated by Django 2.2.9 on 2020-06-02 16:42

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('myparking_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 2, 16, 42, 8, 956626, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateEntreeEffective',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 2, 17, 42, 8, 954628)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateEntreePrevue',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 2, 17, 42, 8, 954628)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateReservation',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 2, 17, 42, 8, 954628)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateSortieEffective',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 2, 17, 42, 8, 954628)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateSortiePrevue',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 2, 17, 42, 8, 954628)),
        ),
        migrations.AlterField(
            model_name='signalement',
            name='dateDebut',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 2, 16, 42, 8, 955627, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='signalement',
            name='dateFin',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 2, 16, 42, 8, 955627, tzinfo=utc)),
        ),
    ]