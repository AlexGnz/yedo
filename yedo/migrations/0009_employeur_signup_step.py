# Generated by Django 2.2 on 2019-09-16 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yedo', '0008_auto_20190916_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeur',
            name='signup_step',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
