# Generated by Django 2.2.9 on 2020-02-15 21:22

from django.db import migrations, models
import django.db.models.deletion
import djongo.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('myparking_api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Terme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenu', models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='parking',
            name='horaire',
        ),
        migrations.AddField(
            model_name='horaire',
            name='Jours',
            field=models.TextField(default='Dimanche - Jeudi'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parking',
            name='horaires',
            field=djongo.models.fields.ArrayReferenceField(blank=True, default=[], on_delete=django.db.models.deletion.CASCADE, to='myparking_api.Horaire'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parking',
            name='termes',
            field=djongo.models.fields.ArrayReferenceField(blank=True, default=[], on_delete=django.db.models.deletion.DO_NOTHING, to='myparking_api.Terme'),
            preserve_default=False,
        ),
    ]