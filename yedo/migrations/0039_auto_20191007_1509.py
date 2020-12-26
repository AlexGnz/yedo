# Generated by Django 2.2 on 2019-10-07 15:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('yedo', '0038_auto_20191007_1250'),
    ]

    operations = [
        migrations.CreateModel(
            name='Diplome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=1000, null=True)),
                ('age', models.IntegerField(blank=True, default=0, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='age',
            field=models.IntegerField(blank=True, default=18, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='domaine',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='diplome',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='yedo.Diplome'),
        ),
    ]
