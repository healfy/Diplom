# Generated by Django 2.0.7 on 2018-08-10 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PokerApp', '0012_auto_20180806_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='positionofcurrentplayer',
            name='status',
            field=models.CharField(max_length=10),
        ),
    ]
