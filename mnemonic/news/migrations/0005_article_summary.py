# Generated by Django 3.0.5 on 2020-04-26 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_auto_20200425_2039'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='summary',
            field=models.TextField(blank=True, null=True),
        ),
    ]
