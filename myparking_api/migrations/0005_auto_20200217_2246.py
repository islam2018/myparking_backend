# Generated by Django 2.2.9 on 2020-02-17 21:46

from django.db import migrations, models
import django.db.models.deletion
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('myparking_api', '0004_auto_20200217_2130'),
    ]

    operations = [
        migrations.AddField(
            model_name='parking',
            name='paiments',
            field=djongo.models.fields.ArrayReferenceField(blank=True, default=[], on_delete=django.db.models.deletion.DO_NOTHING, to='myparking_api.Paiment'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='paiment',
            name='type',
            field=models.TextField(unique=True),
        ),
    ]
