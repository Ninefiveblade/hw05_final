# Generated by Django 2.2.16 on 2022-02-24 17:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_auto_20220224_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата публикации комментария'),
            preserve_default=False,
        ),
    ]
