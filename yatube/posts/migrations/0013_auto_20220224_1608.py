# Generated by Django 2.2.16 on 2022-02-24 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(help_text='Введите текст комментария', verbose_name='Текст комментария'),
        ),
    ]
