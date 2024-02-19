from osgeo import gdal
from osgeo import ogr
import numpy as np
import matplotlib.pyplot as plt


def clip_tiff_with_kml(tiff_path, kml_path, output_path):
    print("Opening KML file...")
    driver = ogr.GetDriverByName('KML')
    kml_ds = driver.Open(kml_path)
    layer = kml_ds.GetLayer()
    feature = layer.GetNextFeature()
    geom = feature.GetGeometryRef().Clone()  
    print("Opening TIFF file...")
    tiff_ds = gdal.Open(tiff_path, gdal.GA_ReadOnly)
    if tiff_ds is None:
        print("Unable to open the TIFF file.")
        return
    print("Performing the clipping...")
    gdal.Warp(output_path, tiff_ds, format='GTiff', cutlineDSName=kml_path,
              cutlineLayer=layer.GetName(), cropToCutline=True)
    kml_ds = None
    tiff_ds = None


def cal_ndvi(clipped):
    open_clipped = gdal.Open(clipped)
    band5  = open_clipped.GetRasterBand(5)
    band5_array = band5.ReadAsArray()
    band4  = open_clipped.GetRasterBand(4)
    band4_array = band4.ReadAsArray()

    xsize = band5.XSize 
    ysize = band5.YSize 

    # Create output raster file
    driver = gdal.GetDriverByName("GTiff")
    out_ds = driver.Create("ndvi.tif", xsize, ysize, 1,
                           gdal.GDT_UInt16,
                           ["COMPRESS=LZW", "PREDICTOR=2",
                            "BIGTIFF=YES"])
    out_ds.SetProjection(open_clipped.GetProjection())
    out_ds.SetGeoTransform(open_clipped.GetGeoTransform())
    out_band = out_ds.GetRasterBand(1)
    out_band.SetNoDataValue(65535)
    ndvi = (band5_array-band4_array)/(band5_array+band4_array)
    out_band.WriteArray(ndvi)

def ndvi_stats(ndvi_img):
    ndvi = gdal.Open(ndvi_img)
    stats = ndvi.GetRasterBand(1)
    return stats.GetStatistics(0,1)
