# Generated by Django 5.1 on 2024-08-31 16:34

import championship.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('championship', '0005_day_match'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='foto',
            field=models.ImageField(upload_to=championship.models.player_image_path),
        ),
    ]
