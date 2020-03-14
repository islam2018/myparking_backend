# Generated by Django 2.2.9 on 2020-02-27 20:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myparking_api', '0002_auto_20200224_1407'),
    ]

    operations = [
        migrations.AddField(
            model_name='automobiliste',
            name='numTel',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateEntreeEffective',
            field=models.DateTimeField(default=datetime.datetime(2020, 2, 27, 21, 29, 45, 509245)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateEntreePrevue',
            field=models.DateTimeField(default=datetime.datetime(2020, 2, 27, 21, 29, 45, 509245)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateSortieEffective',
            field=models.DateTimeField(default=datetime.datetime(2020, 2, 27, 21, 29, 45, 509245)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateSortiePrevue',
            field=models.DateTimeField(default=datetime.datetime(2020, 2, 27, 21, 29, 45, 509245)),
        ),
    ]