# Generated by Django 3.0.5 on 2020-04-25 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_auto_20200425_1915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='tweet_id',
            field=models.BigIntegerField(unique=True),
        ),
    ]
