# Generated by Django 3.2.16 on 2025-01-26 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_auto_20250125_2132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(max_length=20, verbose_name='местоположение'),
        ),
    ]
