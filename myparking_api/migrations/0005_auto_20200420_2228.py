# Generated by Django 2.2.9 on 2020-04-20 21:28

import datetime
from django.db import migrations, models
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('myparking_api', '0004_auto_20200419_2151'),
    ]

    operations = [
        migrations.AddField(
            model_name='automobiliste',
            name='position',
            field=djongo.models.fields.ListField(default=[]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateEntreeEffective',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 20, 22, 27, 51, 942771)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateEntreePrevue',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 20, 22, 27, 51, 942771)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateSortieEffective',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 20, 22, 27, 51, 942771)),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='dateSortiePrevue',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 20, 22, 27, 51, 942771)),
        ),
    ]
