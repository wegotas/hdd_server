from django import forms
# from uploads.core.models import Document


class UploadFileFrom(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()