from django import forms
from hdd_server.models import Document
# from uploads.core.models import Document
# from django.core.models import Document


class UploadFileFrom(forms.Form):
    file = forms.FileField()


class DocumentForm(forms.ModelForm):
    model = Document
    fields = ('document',)
