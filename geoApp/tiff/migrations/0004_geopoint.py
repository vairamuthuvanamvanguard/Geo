# Generated by Django 4.2.9 on 2024-03-04 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tiff', '0003_alter_tiff_uploaded_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('tiff_layer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points', to='tiff.tiff')),
            ],
        ),
    ]
