from django.db import models
import datetime
import tempfile
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
import geopandas as gpd
import boto3
import os
import glob
import zipfile
from sqlalchemy import *
from geo.Geoserver import Geoserver
from pg.pg import Pg

####################################################################################
# Please change the Pg parameters, Geoserver parameters and conn_str
####################################################################################
# initializing the library
db = Pg(dbname='geoapp', user='postgres',
        password='muthu12345', host='database-1.cla06cywkakj.ap-south-1.rds.amazonaws.com', port='5432')
geo = Geoserver('http://127.0.0.1:8080/geoserver', username='admin', password='Skyblue@1002')
# Database connection string (postgresql://${database_user}:${databse_password}@${database_host}:${database_port}/${database_name}
conn_str = 'postgresql://postgres:muthu12345@database-1.cla06cywkakj.ap-south-1.rds.amazonaws.com:5432/geoapp'


######################################################################################
# Shp model
######################################################################################
# The shapefile model
class Shp(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000, blank=True)
    file = models.FileField(upload_to='%Y/%m/%d')
    uploaded_date = models.DateField(default=datetime.date.today, blank=True)

    def __str__(self):
        return self.name

# #########################################################################################
# # Django post save signal
# #########################################################################################
@receiver(post_save, sender=Shp)
def publish_data(sender, instance, created, **kwargs):
    if not created:
        return

    # AWS S3 client setup
    s3_client = boto3.client(
    's3',
    aws_access_key_id='AKIAYS2NV5DW6WVZIGBC',
    aws_secret_access_key='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',
    region_name='ap-south-1'
)

    bucket_name = instance.file.storage.bucket.name
    file_key = instance.file.name
    print("hello")
    # Use a temporary directory to handle the file
    with tempfile.TemporaryDirectory() as tmp_dir:
        local_file_path = os.path.join(tmp_dir, os.path.basename(file_key))

        # Download the file from S3
        s3_client.download_file(bucket_name, file_key, local_file_path)
        print("hello1")
        # Now proceed with your original logic
        file_format = os.path.basename(local_file_path).split('.')[-1]
        file_name = os.path.basename(local_file_path).split('.')[0]
        file_path = tmp_dir
        name = instance.name
        print("hello3")
        # Extract zipfile
        with zipfile.ZipFile(local_file_path, 'r') as zip_ref:
            zip_ref.extractall(file_path)
            print(f"Extracted files to {file_path}")
        extracted_files = os.listdir(file_path)
        print("Extracted files:", extracted_files)


        # Find .shp file in the extracted files
        shp = glob.glob(f'{file_path}/**/*.shp', recursive=True)
        print("Shape files found:", shp)

        try:
            req_shp = shp[0]
            gdf = gpd.read_file(req_shp)  # Make GeoDataFrame
            engine = create_engine(conn_str)
            print("Attempting to write GeoDataFrame to PostGIS")
            gdf.to_postgis(con=engine, schema='data', name=name, if_exists="replace")
            print("Write operation successful")


        except Exception as e:
            print("There is a problem during .shp upload: ", e)
            instance.delete()
            return

        # Publish .shp to the geoserver using geoserver-rest
        geo.create_featurestore(store_name='geoApp', workspace='geoapp', db='geoapp',
                                host='database-1.cla06cywkakj.ap-south-1.rds.amazonaws.com', 
                                pg_user='postgres', pg_password='muthu12345', schema='data')
        print("create operation successful")
        geo.publish_featurestore(workspace='geoapp', store_name='geoApp', pg_table=name)
        print("Publish operation successful")
        geo.create_outline_featurestyle('geoApp_shp', workspace='geoapp')
        geo.publish_style(layer_name=name, style_name='geoApp_shp', workspace='geoapp')

        # # Clean up temporary files
        # for file in os.listdir(file_path):
        #     os.remove(os.path.join(file_path, file))


#########################################################################################
# Django post delete signal
#########################################################################################
@receiver(post_delete, sender=Shp)
def delete_data(sender, instance, **kwargs):
    db.delete_table(instance.name, schema='data')
    geo.delete_layer(instance.name, 'geoapp')
