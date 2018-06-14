from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from website.forms import *
from website.logic import *
from django.core.files.storage import FileSystemStorage

# Create your views here.


@csrf_exempt
def log(request):
    print("log upload")
    if request.method == 'POST':
        form = UploadFileFrom(request.POST, request.FILES)
        if form.is_valid():
            print("Valid")
            hw = HddWriter(request.FILES['file'], request.FILES['file']._name)
            hw.save()
            return render(request, 'success.html')
        else:
            print("Invalid")
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
            file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            uploaded_file_url = fs.url(filename)
            print("uploaded_file_url: " + filename)
            return render(request, 'success.html')
        else:
            print("Invalid")
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
            form.save()
            # file = request.FILES['file']
            # fs = FileSystemStorage()
            # filename = fs.save(file.name, file)
            # uploaded_file_url = fs.url(filename)
            # print("uploaded_file_url: " + uploaded_file_url)
            return render(request, 'success.html')
        else:
            print("Invalid")
    else:
        form = DocumentForm()
        return render(request, 'uploader.html', {'form': form})
