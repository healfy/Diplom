# Generated by Django 2.0.7 on 2018-08-06 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('PokerApp', '0011_gamewithplayers_wage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamewithplayers',
            name='action_flop',
        ),
        migrations.RemoveField(
            model_name='gamewithplayers',
            name='action_river',
        ),
        migrations.RemoveField(
            model_name='gamewithplayers',
            name='action_turn',
        ),
    ]