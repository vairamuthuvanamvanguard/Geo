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


@csrf_exempt
def process_geospatial_data(request):
    if request.method == 'POST':
        try:
            kml_file = request.FILES['kml_file']
            bucket_name = "geoproject1"
            kml_directory = "kml_files"
            ndvi_directory = "ndvi_img"  
            kml_file_key = upload_file_to_s3(kml_file, bucket_name, kml_directory)
            tiff_file_key = "ndvi_dir/clipped_landsat.tif"
            clipped_path_key = "ndvi_clip/clipped.tif"
            success = clip_tiff_with_kml(f'/vsis3/{bucket_name}/{tiff_file_key}', f'/vsis3/{bucket_name}/{kml_file_key}', f'/vsis3/{bucket_name}/{clipped_path_key}')
            if not success:
                return JsonResponse({'status': 'error', 'message': 'Failed to process KML file.'})
            ndvi_file_key = cal_ndvi(f'/vsis3/{bucket_name}/{clipped_path_key}', bucket_name, ndvi_directory)
            stats = ndvi_stats(f'/vsis3/{bucket_name}/{ndvi_file_key}')
            download_url = generate_s3_presigned_url(bucket_name, ndvi_file_key)
            
            return JsonResponse({'status': 'success', 'ndvi_stats': stats, 'download_url': download_url})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred during processing: ' + str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


def generate_s3_presigned_url(bucket_name, object_key):
    s3_client = boto3.client('s3')
    url = s3_client.generate_presigned_url('get_object',
                                           Params={'Bucket': bucket_name, 'Key': object_key},
                                           ExpiresIn=3600)  
    return url




def ndvi_view(request):
    return render(request, 'ndvi.html')
