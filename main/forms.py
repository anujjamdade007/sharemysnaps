from django import forms

class GoogleDriveFolderForm(forms.Form):
    event_name = forms.CharField(max_length=255, required=True, label='Event Name')
    folder_name = forms.CharField(max_length=255, required=True, label='Folder Name')