# Generated by Django 2.0.7 on 2018-07-20 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PokerApp', '0002_currentgame_gamewithplayers'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamewithplayers',
            name='current_stack',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='gamewithplayers',
            name='seat',
            field=models.IntegerField(default=0),
        ),
    ]