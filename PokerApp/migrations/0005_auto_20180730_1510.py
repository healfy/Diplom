# Generated by Django 2.0.7 on 2018-07-30 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PokerApp', '0004_auto_20180730_1259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='currentgame',
            name='big_blind_seat',
        ),
        migrations.RemoveField(
            model_name='currentgame',
            name='small_blind_seat',
        ),
        migrations.RemoveField(
            model_name='gamewithplayers',
            name='seat',
        ),
        migrations.AddField(
            model_name='gamewithplayers',
            name='position',
            field=models.CharField(choices=[('EP', 'EP'), ('MP', 'MP'), ('CO', 'CO'), ('SB', 'SB'), ('BB', 'BB')], default='SB', max_length=10),
        ),
    ]