# Generated by Django 2.2 on 2019-09-16 14:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('yedo', '0006_disponilitytype_intern_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dispo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jours_dispo', models.IntegerField(default=0)),
                ('dispo_explications', models.CharField(blank=True, max_length=500, null=True)),
                ('soiree', models.BooleanField(blank=True, default=False, null=True)),
                ('stage_remunere', models.BooleanField(blank=True, default=False, null=True)),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yedo.DisponilityType')),
            ],
        ),
        migrations.CreateModel(
            name='Employeur',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=500, null=True)),
                ('is_deleted', models.BooleanField(blank=True, default=False, null=True)),
                ('is_visible', models.BooleanField(blank=True, default=True, null=True)),
                ('TVA', models.CharField(blank=True, max_length=50, null=True)),
                ('ville', models.CharField(blank=True, max_length=200, null=True)),
                ('adresse', models.CharField(blank=True, max_length=500, null=True)),
                ('photo', models.FileField(blank=True, default=None, null=True, upload_to='')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='messenger_id',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.IntegerField(blank=True, default=0, null=True)),
                ('employeur', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yedo.Employeur')),
            ],
        ),
        migrations.CreateModel(
            name='Horaires',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin', models.DateTimeField(blank=True, null=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('dispo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yedo.Dispo')),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='notes',
            field=models.ManyToManyField(to='yedo.Rating'),
        ),
    ]
