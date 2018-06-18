from django import forms
from hdd_server.models import Document


class UploadFileFrom(forms.Form):
    document = forms.FileField()


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document',)
