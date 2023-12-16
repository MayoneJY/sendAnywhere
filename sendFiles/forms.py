from django import forms
from .models import File

class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('file', 'file_token')
        
class FilePasswordForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('file_token', 'file_user_password')