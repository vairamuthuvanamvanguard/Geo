from django.shortcuts import render
from django.http import JsonResponse
from .processing import clip_tiff_with_kml, cal_ndvi, ndvi_stats
from .models import Shp
from tiff.models import Tiff
from note.models import Note
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage


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

@csrf_exempt
def process_geospatial_data(request):
    if request.method == 'POST':
        tiff_file = request.FILES['tiff_file']
        kml_file = request.FILES['kml_file']
        tiff_path = default_storage.save('tmp/' + tiff_file.name, tiff_file)
        kml_path = default_storage.save('tmp/' + kml_file.name, kml_file)
        clipped_path = 'tmp/clipped.tif'
        ndvi_path = 'tmp/ndvi.tif'
        clip_tiff_with_kml(tiff_path, kml_path, clipped_path)
        cal_ndvi(clipped_path)
        stats = ndvi_stats(ndvi_path)
        return JsonResponse({'status': 'success', 'ndvi_stats': stats})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def ndvi_view(request):
    return render(request, 'ndvi.html')
