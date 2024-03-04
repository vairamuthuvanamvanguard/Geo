from osgeo import gdal
from osgeo import ogr
import osgeo.gdal_array
import numpy as np
import matplotlib.pyplot as plt
import boto3
from tiff.models import GeoPoint, Tiff
from django.contrib.gis.geos import GEOSGeometry



def clip_tiff_with_kml(tiff_instance, tiff_path, kml_path, output_path):
    print("Attempting to open KML file at path:", kml_path)
    driver = ogr.GetDriverByName('KML')
    kml_ds = driver.Open(kml_path)
    if kml_ds is None:
        print(f"Failed to open KML file at path: {kml_path}")
        return False
    layer = kml_ds.GetLayer()
    if layer is None:
        print(f"No layer found in KML file: {kml_path}")
        return False

    # Loop through features safely and store points in the database
    for feature in layer:
        geom = feature.GetGeometryRef()
        if geom is None:
            print("Feature without geometry encountered.")
            continue  # Skip this feature and continue with the next
        if geom.GetGeometryName() == 'POLYGON':
            # Convert the OGR geometry to a GEOSGeometry for easy handling
            geos_geom = GEOSGeometry(geom.ExportToWkt())
            # Assuming the polygon is simple and you want to store each vertex
            for point in geos_geom.coords[0]:  # Access the outer ring directly
                GeoPoint.objects.create(tiff_layer=tiff_instance, latitude=point[1], longitude=point[0])

    # Reset reading before getting the next feature for clipping
    layer.ResetReading()
    feature = layer.GetNextFeature()
    while feature:
        geom = feature.GetGeometryRef()
        if geom is not None:
            print("Opening TIFF file...")
            tiff_ds = gdal.Open(tiff_path, gdal.GA_ReadOnly)
            if tiff_ds is None:
                print("Unable to open the TIFF file.")
                return False
            print("Performing the clipping...")
            success = gdal.Warp(output_path, tiff_ds, format='GTiff', cutlineDSName=kml_path,
                                cutlineLayer=layer.GetName(), cropToCutline=True)
            if success:
                print("Success on creation")
                return True
            else:
                print("Failed to clip the TIFF file.")
                return False
        feature = layer.GetNextFeature()

    print("No valid geometry found in any KML feature.")
    return False




def cal_ndvi(clipped, bucket_name, ndvi_directory):
    print("file", clipped)
    open_clipped = gdal.Open(clipped)
    band5 = open_clipped.GetRasterBand(5)
    band5_array = band5.ReadAsArray()
    band4 = open_clipped.GetRasterBand(4)
    band4_array = band4.ReadAsArray()
    xsize = band5.XSize
    ysize = band5.YSize
    local_ndvi_path = "/tmp/ndvi.tif"
    driver = gdal.GetDriverByName("GTiff")
    out_ds = driver.Create(local_ndvi_path, xsize, ysize, 1, gdal.GDT_UInt16, ["COMPRESS=LZW", "PREDICTOR=2", "BIGTIFF=YES"])
    out_ds.SetProjection(open_clipped.GetProjection())
    out_ds.SetGeoTransform(open_clipped.GetGeoTransform())
    out_band = out_ds.GetRasterBand(1)
    out_band.SetNoDataValue(65535)
    ndvi = (band5_array - band4_array) / (band5_array + band4_array)
    out_band.WriteArray(ndvi)
    out_ds = None
    open_clipped = None
    s3_client = boto3.client('s3')
    ndvi_file_key = f'{ndvi_directory}/ndvi.tif'
    s3_client.upload_file(local_ndvi_path, bucket_name, ndvi_file_key)
    print("NDVI TIFF uploaded to S3")
    return ndvi_file_key


def ndvi_stats(ndvi_img):
    ndvi = gdal.Open(ndvi_img)
    stats = ndvi.GetRasterBand(1)
    return stats.GetStatistics(0,1)
