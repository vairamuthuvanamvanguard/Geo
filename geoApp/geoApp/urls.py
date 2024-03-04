"""geoApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from shp.views import index, data_api
from shp.views import process_geospatial_data, ndvi_view,upload_clipped_tiff_and_create_geodata, get_tiff_layer_points
from note.views import note
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('note/', note, name='note'),
    path('geospace', process_geospatial_data, name='process_geospatial_data'),
    path('ndvi', ndvi_view, name='ndvi'),  
    path('api/data/', data_api, name='data_api'),
    path('tiffupload', upload_clipped_tiff_and_create_geodata, name='tiffupload'),  
    path('api/tiff-layer/<str:layer_name>/points/', get_tiff_layer_points, name='tiff_layer_points'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
