# Generated by Django 2.2 on 2019-10-06 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yedo', '0036_student_permis'),
    ]

    operations = [
        migrations.AddField(
            model_name='zip',
            name='name_fr',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='zip',
            name='name_nl',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
