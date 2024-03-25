from django import forms

class LinkUploadForm(forms.Form):
    url = forms.URLField(label="File URL", required=True)
    
    
class QueryForm(forms.Form):
    querry = forms.CharField(label="Question", required=True)