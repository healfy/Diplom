# Generated by Django 2.0.7 on 2018-07-30 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PokerApp', '0007_auto_20180730_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentgame',
            name='big_blind_seat',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='currentgame',
            name='small_blind_seat',
            field=models.IntegerField(default=0),
        ),
    ]
