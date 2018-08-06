from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from website.forms import *
from website.logic import *
from django.core.files.storage import FileSystemStorage
import tarfile

# Create your views here.


@csrf_exempt
def lot_content(request, int_index):
    if request.method == 'POST':
        print('POST method')
    if request.method == 'GET':
        print('GET method')
        # print(request.GET)
        lch = LotContentHolder(int_index)
        lch.filter(request.GET.copy())
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
        elif 'hdds' in request.GET:
            hh = HddHolder()
            hh.filter(request.GET.copy())
            return render(request, 'index.html', {'hh': hh})
        elif 'orders' in request.GET:
            # oh = 'placeholder'
            oh = OrdersHolder()
            return render(request, 'index.html', {'oh': oh})
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
def hdd_delete(request, int_index):
    print('hdd_delete')
    htd = HddToDelete(pk=int_index)
    if request.method == 'POST':
        print('POST method')
        htd.delete()
        if htd.success:
            print('success')
            return render(request, 'success.html')
        else:
            print('Failed deletion')
            print(htd.message)
            return render(request, 'failure.html', {'message': htd.message}, status=404)
    if request.method == 'GET':
        print('GET method')
        return HttpResponse('<p>You should not be here.</p><p>What are you doing over here?</p>', status=404)


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
            tp = TarProcessor(request.FILES['document'])
            tp.process_data()
            return render(request, 'success.html')
        else:
            print("Invalid")
            return render(request, 'uploader.html', {'form': form})
    else:
        form = DocumentForm()
        return render(request, 'uploader.html', {'form': form})


@csrf_exempt
def order(request):
    print("order upload")
    if request.method == 'POST':
        '''
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            print("Valid")
            tp = TarProcessor(request.FILES['document'])
            tp.process_data()
            return render(request, 'success.html')
        else:
            print("Invalid")
            return render(request, 'uploader.html', {'form': form})
        '''
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            print("Valid")
            op = OrderProcessor(request.FILES['document'])
            return HttpResponse('This page supposed to be thrown out after successful operation')
        else:
            print("Invalid")
            return render(request, 'uploader.html', {'form': form})
    else:
        form = DocumentForm()
        return render(request, 'uploader.html', {'form': form})


def view_pdf(request, int_index):
    print('Index is: ' + str(int_index))
    print('view_pdf')
    pv = PDFViewer(int_index)
    if request.method == 'POST':
        print('POST request')
    elif request.method == 'GET':
        print('GET request')
        return HttpResponse(pv.pdf_content, content_type='application/pdf')
