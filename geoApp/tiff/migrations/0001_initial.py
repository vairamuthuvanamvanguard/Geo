# Generated by Django 4.2.9 on 2024-01-26 12:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tiff",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("description", models.CharField(blank=True, max_length=1000)),
                ("file", models.FileField(upload_to="%Y/%m/%d")),
                (
                    "uploaded_date",
                    models.DateField(blank=True, default=datetime.date.today),
                ),
            ],
        ),
    ]
