# Generated by Django 4.2.19 on 2025-03-01 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seoapp', '0004_crawlresult_backlinks_crawlresult_external_links_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='plan',
            field=models.CharField(default='Free', max_length=20),
        ),
    ]
