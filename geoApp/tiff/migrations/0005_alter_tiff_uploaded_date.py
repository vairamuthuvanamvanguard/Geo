# Generated by Django 4.2.9 on 2024-03-04 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tiff', '0004_geopoint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tiff',
            name='uploaded_date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
