from django.shortcuts import render
from django.http import JsonResponse
from .processing import clip_tiff_with_kml, cal_ndvi, ndvi_stats
from .models import Shp, GeoData
from tiff.models import Tiff
from note.models import Note
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import os
from django.conf import settings
import boto3
from geo.Geoserver import Geoserver
import tempfile

geo = Geoserver('http://localhost:8080/geoserver', username='admin', password='Skyblue@1002')
s3_client = boto3.client(
    's3',
   aws_access_key_id='AKIAYS2NV5DW6WVZIGBC',
    aws_secret_access_key='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',
    region_name='ap-south-1'
)

def index(request):
    shp = Shp.objects.all()
    tiff = Tiff.objects.all()
    note = Note.objects.all()
    return render(request, 'index.html', {'shp': shp, 'tiff': tiff, 'note': note})


def note(request):
    if(request.method == 'POST'):
        note_heading = request.POST.get('note-heading')
        note = request.POST.get('note')
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        print(note_heading, note, lat, lng, 'email username')
        return render(request, 'index.html')
    return render(request, 'index.html')


def upload_file_to_s32(file_path, object_name=None):
    """
    Upload a file to an S3 bucket, placing it within the 'ndvi_dir' directory.

    :param file_path: File to upload
    :param bucket_name: Bucket to upload to
    :param object_name: S3 object name. If not specified, file_path is used
    :return: The S3 key of the uploaded file if successful, else None
    """
    bucket_name="geoproject1"
    if object_name is None:
        object_name = 'ndvi_dir/' + file_path.split('/')[-1]
    else:
        object_name = 'ndvi_dir/' + object_name
    s3_client = boto3.client(
        's3',
        aws_access_key_id='AKIAYS2NV5DW6WVZIGBC',
        aws_secret_access_key='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',
        region_name='ap-south-1'
    )
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        return object_name
    except Exception as e:
        print(f"Upload failed: {e}")
        return None


@csrf_exempt
def upload_clipped_tiff_and_create_geodata(request):
    if request.method == 'POST':
        tiff_file_path = "clipped_landsat.tif"  
        tiff_file_key = upload_file_to_s32(tiff_file_path)
        if tiff_file_key:
            print("S3 upload successful, attempting to create GeoData entry...")
            geodata = GeoData.objects.create(
                tiff_file_key=tiff_file_key,
            )
            return JsonResponse({'status': 'success', 'message': f'GeoData entry created with TIFF file key: {tiff_file_key}'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to upload TIFF file to S3 and create GeoData entry.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})




def upload_file_to_s3(file_obj, bucket_name, directory):
    """
    Upload an InMemoryUploadedFile to S3 and return the key.
    """
    s3_client = boto3.client('s3', aws_access_key_id='AKIAYS2NV5DW6WVZIGBC',
                             aws_secret_access_key='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',
                             region_name='ap-south-1')
    file_key = f'{directory}/{file_obj.name}'
    s3_client.upload_fileobj(file_obj, bucket_name, file_key)
    return file_key

    

def process_and_store_geospatial_data(kml_path, tiff_path, ndvi_path, stats):
    """
    Process geospatial data, store in S3, and save references in the database.
    """
    kml_file_key = upload_file_to_s3(kml_path)
    tiff_file_key = upload_file_to_s3(tiff_path)
    ndvi_file_key = upload_file_to_s3(ndvi_path)
    geo_data = GeoData.objects.create(
        kml_file=kml_file_key,
        tiff_file=tiff_file_key,
        ndvi_file=ndvi_file_key,
        stats=stats
    )
    return geo_data

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


def publish_tiff_to_geoserver(tiff_instance, file_key, workspace, layer_name):
    """
    Downloads a TIFF file from S3, publishes it to GeoServer, and updates the Tiff model instance.

    :param tiff_instance: The Tiff model instance to update with publication details.
    :param file_key: The S3 key of the TIFF file.
    :param workspace: The GeoServer workspace to publish the layer in.
    :param layer_name: The name of the layer to be created in GeoServer.
    :return: True if the publication was successful, False otherwise.
    """
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            local_file_path = os.path.join(tmp_dir, os.path.basename(file_key))
            s3_client.download_file("geoproject1", file_key, local_file_path)

            if geo.create_coveragestore(local_file_path, workspace=workspace, layer_name=layer_name) and \
               geo.create_coveragestyle(local_file_path, style_name=layer_name, workspace=workspace) and \
               geo.publish_style(layer_name=layer_name, style_name=layer_name, workspace=workspace):
                
                tiff_instance.is_published_to_geoserver = True
                tiff_instance.geoserver_workspace = workspace
                tiff_instance.geoserver_layer_name = layer_name
                tiff_instance.save()
                print("published to geoserver")

                return True
            else:
                print("Failed to publish to GeoServer.")
                return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False



@csrf_exempt
def process_geospatial_data(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    try:
        kml_file = request.FILES.get('kml_file')
        if not kml_file:
            return JsonResponse({'status': 'error', 'message': 'No KML file provided.'}, status=400)

        bucket_name = "geoproject1"
        kml_file_key = upload_file_to_s3(kml_file, bucket_name, "kml_files")
        tiff_file_key = "ndvi_dir/clipped_landsat.tif"
        clipped_path_key = "ndvi_clip/clipped.tif"

        if not clip_tiff_with_kml(f'/vsis3/{bucket_name}/{tiff_file_key}', f'/vsis3/{bucket_name}/{kml_file_key}', f'/vsis3/{bucket_name}/{clipped_path_key}'):
            return JsonResponse({'status': 'error', 'message': 'Failed to process KML file.'}, status=500)

        ndvi_file_key = cal_ndvi(f'/vsis3/{bucket_name}/{clipped_path_key}', bucket_name, "ndvi_img")
        tiff_instance = Tiff.objects.create(
            name='ndvi_img',
            description='Description of what the TIFF represents',
            file=ndvi_file_key  # Adjust based on your actual file handling
        )

        stats = ndvi_stats(f'/vsis3/{bucket_name}/{ndvi_file_key}')
        download_url = generate_s3_presigned_url(bucket_name, ndvi_file_key)

        # Assuming `publish_tiff_to_geoserver` wraps the GeoServer publishing logic
        if publish_tiff_to_geoserver(tiff_instance, ndvi_file_key, 'geoapp', 'ndvi_layer'):
            # Handle success
            return JsonResponse({'status': 'success', 'message': 'TIFF published to GeoServer.','ndvi_stats': stats,})
        else:
            # Handle failure
            return JsonResponse({'status': 'error', 'message': 'Failed to publish TIFF to GeoServer.'}, status=500)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An error occurred during processing: {str(e)}'}, status=500)



def generate_s3_presigned_url(bucket_name, object_key):
    s3_client = boto3.client('s3')
    url = s3_client.generate_presigned_url('get_object',
                                           Params={'Bucket': bucket_name, 'Key': object_key},
                                           ExpiresIn=3600)  
    return url




def ndvi_view(request):
    return render(request, 'ndvi.html')
