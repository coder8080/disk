# Generated by Django 3.1.1 on 2020-10-26 07:38

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_publicfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publicfile',
            name='url',
            field=models.CharField(default=main.models.generate_token, max_length=1000, verbose_name='Уникальный код'),
        ),
    ]