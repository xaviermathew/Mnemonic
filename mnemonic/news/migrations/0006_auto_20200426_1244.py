# Generated by Django 3.0.5 on 2020-04-26 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0005_article_summary'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='is_pushed_to_index',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tweet',
            name='is_pushed_to_index',
            field=models.BooleanField(default=False),
        ),
    ]
