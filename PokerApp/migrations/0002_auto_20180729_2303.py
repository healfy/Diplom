# Generated by Django 2.0.7 on 2018-07-29 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PokerApp', '0001_initial'),
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