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
from pg.pg import Pg
from django.db import models



# Database and GeoServer initialization

geo = Geoserver('http://172.30.139.139:8080/geoserver', username='admin', password='Skyblue@1002')
conn_str = 'postgresql://postgres:muthu12345@localhost'


s3_client = boto3.client(
    's3',
   aws_access_key_id='AKIAYS2NV5DW6WVZIGBC',
    aws_secret_access_key='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',
    region_name='ap-south-1'
)

db = Pg(dbname='geoapp', user='postgres',
        password='muthu12345', host='localhost', port='5432')


####################################################################################
# Please change the Pg parameters, Geoserver parameters and conn_str
####################################################################################
# initializing the library

geo = Geoserver('http://15.206.186.153:8080/geoserver', username='admin', password='Skyblue@1002')
# Database connection string (postgresql://${database_user}:${databse_password}@${database_host}:${database_port}/${database_name}
conn_str = 'postgresql://postgres:muthu12345@localhost:5432/geoapp'


######################################################################################
# Shp model
######################################################################################
# The shapefile model
class Shp(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000, blank=True)
    file = models.FileField(upload_to='shps/%Y/%m/%d')
    uploaded_date = models.DateField(default=datetime.date.today, blank=True)

    def __str__(self):
        return self.name
    

class GeoData(models.Model):
    kml_file_key = models.CharField(max_length=255, blank=True, null=True)
    tiff_file_key = models.CharField(max_length=255, blank=True, null=True)
    ndvi_file_key = models.CharField(max_length=255, blank=True, null=True)
    stats = models.JSONField(null=True, blank=True)  # Allow null values
    created_at = models.DateTimeField(auto_now_add=True)







# #########################################################################################
# # Django post save signal
# #########################################################################################
@receiver(post_save, sender=Shp)
def publish_data(sender, instance, created, **kwargs):
    if not created:
        return

    file_key = instance.file.name
    bucket_name = 'geoproject1'  # Update with your actual bucket name

    with tempfile.TemporaryDirectory() as tmp_dir:
        local_file_path = os.path.join(tmp_dir, os.path.basename(file_key))

        # Download the file from S3
        s3_client.download_file(bucket_name, file_key, local_file_path)

        # Extract the zipfile
        with zipfile.ZipFile(local_file_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)

        # Find .shp file in the extracted files
        shp_files = glob.glob(f'{tmp_dir}/**/*.shp', recursive=True)
        if not shp_files:
            raise ValueError("No .shp file found in the uploaded zipfile.")

        req_shp = shp_files[0]
        gdf = gpd.read_file(req_shp)  # Make GeoDataFrame

        # Update `conn_str` with your actual database connection string
        conn_str = 'postgresql://postgres:muthu12345@localhost:5432/geoapp'
        engine = create_engine(conn_str)

        # Write GeoDataFrame to PostGIS
        gdf.to_postgis(name=instance.name, con=engine, schema='data', if_exists="replace")

        # Publish .shp to the GeoServer
        geo.create_featurestore(store_name='geoApp', workspace='geoapp', db='geoapp',
                                host='localhost', 
                                pg_user='postgres', pg_password='muthu12345', schema='data')  # Adjusted 'schema' to 'public'
        geo.publish_featurestore(workspace='geoapp', store_name='geoApp', pg_table=instance.name)
        geo.create_outline_featurestyle('geoApp_shp', workspace='geoapp')
        geo.publish_style(layer_name=instance.name, style_name='geoApp_shp', workspace='geoapp')




#########################################################################################
# Django post delete signal
#########################################################################################
@receiver(post_delete, sender=Shp)
def delete_data(sender, instance, **kwargs):
    # Delete the file from S3
    # s3_client.delete_object(Bucket='geoproject1', Key=instance.file.name)

    # Delete table and layer from GeoServer and PostGIS
    db.delete_table(instance.name, schema='data')
    geo.delete_layer(instance.name, 'geoapp')


