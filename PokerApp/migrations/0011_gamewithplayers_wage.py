# Generated by Django 2.0.7 on 2018-08-05 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PokerApp', '0010_positionofcurrentplayer'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamewithplayers',
            name='wage',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
