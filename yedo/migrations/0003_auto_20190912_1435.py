# Generated by Django 2.2 on 2019-09-12 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yedo', '0002_auto_20190912_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='fb_pic',
            field=models.CharField(blank=True, default='', max_length=5000, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='gender',
            field=models.CharField(blank=True, default='male', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='language',
            field=models.CharField(blank=True, default='fr_FR', max_length=20, null=True),
        ),
    ]
