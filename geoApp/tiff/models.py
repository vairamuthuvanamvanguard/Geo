import os
import datetime
import zipfile
import tempfile
import boto3
import glob

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


import geopandas as gpd
from sqlalchemy import create_engine

from geo.Geoserver import Geoserver

s3_client = boto3.client(
    's3',
   aws_access_key_id='AKIAYS2NV5DW6WVZIGBC',
    aws_secret_access_key='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',
    region_name='ap-south-1'
)

# Initialize GeoServer
geo = Geoserver('http://127.0.0.1:8080/geoserver', username='admin', password='Skyblue@1002')

# TIFF Model
class Tiff(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000, blank=True)
    file = models.FileField(upload_to='tiffs/%Y/%m/%d/')
    uploaded_date = models.DateField(default=datetime.date.today, blank=True)

    def __str__(self):
        return self.name

# Post-save Signal for Tiff
@receiver(post_save, sender=Tiff)
def publish_data(sender, instance, created, **kwargs):
    if not created:
        return

    file_key = instance.file.name

    with tempfile.TemporaryDirectory() as tmp_dir:
        local_file_path = os.path.join(tmp_dir, os.path.basename(file_key))

        # Download the file from S3
        s3_client.download_file('geoproject1', file_key, local_file_path)

        # Publish TIFF file to GeoServer
        geo.create_coveragestore(local_file_path, workspace='geoapp', layer_name=instance.name)
        geo.create_coveragestyle(local_file_path, style_name=instance.name, workspace='geoapp')
        geo.publish_style(layer_name=instance.name, style_name=instance.name, workspace='geoapp')

# Post-delete Signal for Tiff
@receiver(post_delete, sender=Tiff)
def delete_data(sender, instance, **kwargs):
    # Delete the file from S3
    # s3_client.delete_object(Bucket='geoproject1', Key=instance.file.name)

    # Delete layer from GeoServer
    geo.delete_layer(instance.name, 'geoapp')
