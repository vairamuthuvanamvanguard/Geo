 # Import the library
from geo.Geoserver import Geoserver

# Initialize the library
geo = Geoserver('http://127.0.0.1:8080/geoserver', username='admin', password='Skyblue@1002')

# For creating workspace
# geo.create_workspace(workspace='demo')
# geo.create_coveragestore(layer_name='layer1', path=r'../frontend/data/clipped.tif', workspace='demo')

# geo.create_featurestore(store_name='geo_data', workspace='demo', db='postgres', host='localhost', pg_user='postgres',
#                         pg_password='muthu12345')

# geo.create_featurestore('postgis', workspace='demo', db='postgres', pg_user='postgres', pg_password='muthu12345', host='127.0.0.1')

# geo.publish_featurestore(store_name='postgis', pg_table='jamoat-db', workspace='demo')


# geo.upload_style(path=r'C:\Users\mvair\Downloads\geoproject\data\style\raster1.sld', workspace='demo')

# geo.publish_style(layer_name='layer1', style_name='raster-new', workspace='demo')

# geo.create_coveragestyle(raster_path=r'../frontend/data/clipped.tif',
#  style_name='raster-new', workspace='demo', color_ramp='hsv')

# geo.create_outline_featurestyle('polygon-style', workspace='demo')
geo.publish_style(layer_name='layer1',
                  style_name='polygon-style', workspace='demo')