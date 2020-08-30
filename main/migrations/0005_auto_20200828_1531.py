# Generated by Django 3.1 on 2020-08-28 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20200824_1743'),
    ]

    operations = [
        migrations.DeleteModel(
            name='File',
        ),
        migrations.AlterField(
            model_name='disk',
            name='allSize',
            field=models.IntegerField(default=5000000000, verbose_name='Всё место на диске пользователя'),
        ),
        migrations.AlterField(
            model_name='disk',
            name='size',
            field=models.IntegerField(default=0, verbose_name='Занятое на диске место'),
        ),
    ]