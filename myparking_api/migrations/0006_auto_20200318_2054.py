# Generated by Django 2.2.9 on 2020-03-18 19:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myparking_api', '0005_auto_20200318_2041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='dateEntreeEffective',
            field=models.DateTimeField(default=datetime.datetime(2020, 3, 18, 20, 54, 27, 40771)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateEntreePrevue',
            field=models.DateTimeField(default=datetime.datetime(2020, 3, 18, 20, 54, 27, 40771)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateSortieEffective',
            field=models.DateTimeField(default=datetime.datetime(2020, 3, 18, 20, 54, 27, 40771)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateSortiePrevue',
            field=models.DateTimeField(default=datetime.datetime(2020, 3, 18, 20, 54, 27, 40771)),
        ),
    ]
