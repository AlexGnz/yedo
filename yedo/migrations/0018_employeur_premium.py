# Generated by Django 2.2 on 2019-09-18 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yedo', '0017_employeur_interest_in_plan3'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeur',
            name='premium',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
