from geo.Geoserver import Geoserver

# Initialize the library with your GeoServer details
geo = Geoserver('http://localhost:8080/geoserver', username='admin', password='geoserver')

# try:
#     geo.create_workspace(workspace='geoapp')
#     print("Workspace 'geoapp' created successfully.")
# except Exception as e:
#     print(f"Failed to create workspace 'geoapp': {e}")

# try:
#     geo.create_coveragestore(layer_name='layer1', path=r'./ndvi.tif', workspace='geoapp')
#     print("CoverageStore 'layer1' created successfully.")
# except Exception as e:
#     print(f"Failed to create CoverageStore 'layer1': {e}")

# try:
#     geo.create_featurestore(store_name='geoApp', workspace='geoapp', db='postgres', host='localhost',
#                             pg_user='postgres', pg_password='muthu12345')
#     print("FeatureStore 'geoApp' created successfully.")
# except Exception as e:
#     print(f"Failed to create FeatureStore 'geoApp': {e}")

# Uncomment and update the path and names as necessary for additional operations
# try:
#     geo.upload_style(path=r'C:\Users\mvair\Downloads\geoproject\data\style\raster1.sld', workspace='demo')
#     print("Style uploaded successfully.")
# except Exception as e:
#     print(f"Failed to upload style: {e}")

# try:
#     geo.publish_style(layer_name='layer1', style_name='raster-new', workspace='demo')
#     print("Style published successfully.")
# except Exception as e:
#     print(f"Failed to publish style: {e}")

# Add more try-except blocks as necessary for other operations
