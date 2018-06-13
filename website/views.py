from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from website.forms import UploadFileFrom
from website.logic import *

# Create your views here.


@csrf_exempt
def index(request):
    print("Index")
    if request.method == 'POST':
        form = UploadFileFrom(request.POST, request.FILES)
        if form.is_valid():
            print("Valid")
            hw = HddWriter(request.FILES['file'])
            hw.save()
            return render(request, 'success.html')
        else:
            print("Invalid")
    else:
        form = UploadFileFrom()
        return render(request, 'index.html', {'form': form})
