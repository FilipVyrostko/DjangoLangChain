from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import LinkUploadForm, QueryForm
from .chat.pinecone.vector_store import add_documents_from_pdf
from .models import PdfFile
from .chat.model.chat import build_chat
import validators, pdfkit, uuid, os


def index(request):
    """
    Renders the index template.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: A response that renders the index template.
    """
    return render(
        request=request,
        template_name='index.html'
    )
    
    
def user_register(request):
    """
    Register a new user

    If the request method is GET, return a rendered register.html template with an unbound
    UserCreationForm in the context.

    If the request method is POST, attempt to create a new user with the provided form data.
    If the form is valid, create the user and log them in. If the form is not valid, return a
    rendered register.html template with the bound form in the context and form errors in the
    context.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: A response that renders the register.html template
    """
    if request.method == 'GET':
        return render(
            request=request,
            template_name='register.html',
            context={'form': UserCreationForm()}
        )

    if request.method == 'POST':        
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=True)
                login(request, user)
                return redirect('index')
            
            except IntegrityError:
                return render(
                    request=request,
                    template_name='register.html',
                    context={'form': UserCreationForm(), 'error': 'User already exists'}
                )
        else:
            return render(
                request=request,
                template_name='register.html',
                context={'form': form, "error": form.errors}
            )

            

def user_login(request):
    """
    Login a user

    If the request method is GET, return a rendered login.html template with an unbound
    AuthenticationForm in the context.

    If the request method is POST, attempt to authenticate the user with the provided form
    data. If the form is valid, log the user in and redirect them to the index view. If the
    form is not valid, return a rendered login.html template with the bound form in the
    context and an error message in the context.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: A response that renders the login.html template
    """
    if request.method == "GET":
        return render(request,
                      template_name='login.html',
                      context={'form': AuthenticationForm()})
        
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is None:
                # Invalid credentials
                return render(request,
                              template_name='login.html',
                              context={'form': form, 'error': 'Invalid credentials'})
            if not user.is_active:
                # Inactive account
                return render(request,
                              template_name='login.html',
                              context={'form': form, 'error': 'Account inactive'})
                
            login(request, user)
            return redirect('index')
        
        else:
            # Invalid form
            return render(request,
                          template_name='login.html',
                          context={'form': form, "error": "Invalid form"})
            

@login_required
def user_logout(requset):
    """
    Logs the user out and redirects them to the index page

    Args:
        requset (HttpRequest): The request object

    Returns:
        HttpResponse: A response that redirects the user to the index page
    """
    logout(requset)
    # Redirect the user to the index page after logging them out
    return render(requset, template_name='index.html')

@login_required
def upload_link(request):
    """
    View function for handling link upload form.

    If the request method is GET, then render the upload_link.html template
    with an empty form.

    If the request method is POST, then handle the form data.
    """
    if request.method == "GET":
        return render(request=request, 
                      template_name='upload_link.html',
                      context={'form': LinkUploadForm()})
    
    # 1. Validate URL
    # 2. Convert to PDF
    # 3. Save to Pinecone
    # 4. Save PDF entry to Django db
    if request.method == "POST":
        form = LinkUploadForm(request.POST)
        """
        Handle form data if form is valid.

        If the URL is valid, then convert the URL to a PDF, save the PDF to
        disk, add the PDF document to Pinecone, and save the PDF entry to the
        Django db.

        If the URL is invalid, then render the upload_link.html template with
        an error message.
        """
        if form.is_valid():
            if validators.url(form.cleaned_data['url']):
                pdf_id = uuid.uuid4()
                pdfkit.from_url(form.cleaned_data['url'], f"pdfs/{pdf_id}.pdf")
                # Add document to Pinecone
                pinecone_id_list = add_documents_from_pdf(
                    pdf_path=f"pdfs/{pdf_id}.pdf",
                    pdf_id=pdf_id
                )
                
                if not pinecone_id_list:
                    return render(request=request, 
                                  template_name='upload_link.html',
                                  context={'form': form, 'error': 'Failed to add document to Pinecone'})
                
                
                # Add document to Django db
                pdf_file = PdfFile.objects.create(
                    user=request.user,
                    pdf_id=pdf_id,
                    pinecone_id_list = pinecone_id_list
                )
                pdf_file.save()
                
            else:
                return render(request=request, 
                              template_name='upload_link.html',
                              context={'form': form, 'error': 'Invalid URL'})
            
        else:
            return render(request=request, 
                          template_name='upload_link.html',
                          context={'form': form, "errors": form.errors})
        
        return redirect('index')

@login_required
def list_documents(request):
    """View function for listing documents.

    Returns:
        Rendered template with a list of PDF documents associated with
        the currently logged in user.
    """
    pdfs = PdfFile.objects.filter(user=request.user)
    return render(request,
                  template_name='list_documents.html',
                  context={'pdfs': pdfs})



@login_required
def view_document(request):
    """View function for viewing a single PDF document.

    Retrieves the PDF document associated with the provided pdf_id parameter
    and renders it in the view_document.html template.

    Args:
        request (django.http.HttpRequest): The request object.

    Returns:
        Rendered template with a single PDF document.
    """
    pdf_id = request.GET.get('pdf_id')
    pdf = PdfFile.objects.get(user=request.user, pdf_id=pdf_id)
    return render(request,
                  template_name='view_document.html',
                  context={'pdf': pdf})


@login_required
def delete_document(request):
    """Delete the PDF document associated with the provided pdf_id.

    This view function deletes the PDF document associated with the
    provided pdf_id GET parameter and redirects the user to the list of
    documents view.

    Args:
        request (django.http.HttpRequest): The request object.

    Returns:
        Redirect to the list of documents view.
    """
    pdf_id = request.GET.get('pdf_id')
    pdf = PdfFile.objects.get(user=request.user, pdf_id=pdf_id)

    # Delete the PDF document from the Django db and file system
    pdf.delete()

    # Redirect the user to the list of documents view
    return redirect('list_documents')


@login_required
def chat_view(request):
    """View function for handling chat view GET and POST requests.

    If the request method is GET, then render the chat_view.html template
    with an empty form.

    If the request method is POST, then handle the form data.
    """
    if request.method == "GET":
        pdf_id = request.GET.get('pdf_id')
        pdf_path = f"pdfs/{pdf_id}.pdf"
        
        return render(
            request, 
            template_name='chat_view.html', 
            context={"pdf_path": pdf_path, "form": QueryForm()})

    if request.method == "POST":
        form = QueryForm(request.POST)
        pdf_id = request.GET.get('pdf_id')
        pdf_path = f"pdfs/{pdf_id}.pdf"

        # Invoke the chat LLM and get the response
        llm_response = ""
        if form.is_valid():
            chat = build_chat(pdf_id)
            reply = chat.invoke({"input": form.cleaned_data['querry']})
            llm_response = reply["answer"]

        # Render the chat_view.html template with the form and response
        return render(request, 
                      template_name='chat_view.html', 
                      context={"pdf_path": pdf_path,
                               "llm_response": llm_response, 
                               "form": form})




