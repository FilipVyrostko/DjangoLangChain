from django import forms

class LinkUploadForm(forms.Form):
    """
    Form for uploading a link to a file.

    Attributes:
        url: URL to the file.

    """
    url = forms.URLField(label="File URL", required=True)
    
    
class QueryForm(forms.Form):
    """
    Form for asking a question.

    Attributes:
        querry: The question to be asked.

    """
    querry = forms.CharField(label="Question", required=True)
