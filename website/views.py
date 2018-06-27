from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from website.forms import *
from website.logic import *
from django.core.files.storage import FileSystemStorage

# Create your views here.


@csrf_exempt
def lot_content(request, int_index):
    if request.method == 'POST':
        print('POST method')
    if request.method == 'GET':
        print('GET method')
        lch = LotContentHolder(int_index)
        return render(request, 'lot_content.html', {'lch': lch})


@csrf_exempt
def index(request):
    print("INDEX")
    if request.method == 'GET':
        print('GET method')
        if 'lots' in request.GET:
            lh = LotsHolder()
            lh.filter(request.GET.copy())
            return render(request, 'index.html', {'lh': lh})
        if 'hdds' in request.GET:
            hh = HddHolder()
            hh.filter(request.GET.copy())
            return render(request, 'index.html', {'hh': hh})
    if request.method == 'POST':
        print('POST method')
    return render(request, 'index.html')


@csrf_exempt
def hdd_edit(request, int_index):
    print('hdd_edit')
    hte = HddToEdit(int_index)
    if request.method == 'POST':
        print('POST method')
        hte.process_edit(int_index, request.POST.copy())
        return render(request, 'success.html')
    if request.method == 'GET':
        print('GET method')
        return render(request, 'hdd_edit.html', {'hte': hte})


@csrf_exempt
def log(request):
    print("log upload")
    if request.method == 'POST':
        form = UploadFileFrom(request.POST, request.FILES)
        if form.is_valid():
            print("Valid")
            hw = HddWriter(request.FILES['document'], request.FILES['document']._name)
            hw.save()
            return render(request, 'success.html')
        else:
            print("Invalid")
            return render(request, 'uploader.html', {'form': form})
    else:
        form = UploadFileFrom()
        return render(request, 'uploader.html', {'form': form})


@csrf_exempt
def pdf(request):
    print("pdf upload")
    if request.method == 'POST':
        form = UploadFileFrom(request.POST, request.FILES)
        if form.is_valid():
            print("Valid")
            file = request.FILES['document']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            uploaded_file_url = fs.url(filename)
            print("uploaded_file_url: " + filename)
            return render(request, 'success.html')
        else:
            print("Invalid")
            return render(request, 'uploader.html', {'form': form})
    else:
        form = UploadFileFrom()
        return render(request, 'uploader.html', {'form': form})


@csrf_exempt
def tar(request):
    print("tar upload")
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            print("Valid")
            print(form.data)
            # form.save()
            # file = request.FILES['file']
            # fs = FileSystemStorage()
            # filename = fs.save(file.name, file)
            # uploaded_file_url = fs.url(filename)
            # print("uploaded_file_url: " + uploaded_file_url)
            return render(request, 'success.html')
        else:
            print("Invalid")
            return render(request, 'uploader.html', {'form': form})
    else:
        form = DocumentForm()
        return render(request, 'uploader.html', {'form': form})