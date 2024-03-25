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
    return render(
        request=request,
        template_name='index.html'
    )
    
    
def user_register(request):
    
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
            if not user:
                return render(request,
                              template_name='login.html',
                              context={'form': form, 'error': 'Invalid credentials'})
            if not user.is_active:
                return render(request,
                              template_name='login.html',
                              context={'form': form, 'error': 'Account inactive'})
                
            login(request, user)
            return redirect('index')
        
        else:
            return render(request,
                          template_name='login.html',
                          context={'form': form, "error": "Invalid form"})
            

@login_required
def user_logout(requset):
    logout(requset)
    return render(requset, template_name='index.html')

@login_required
def upload_link(request):
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
def list_documents(requst):
    pdfs = PdfFile.objects.filter(user=requst.user)
    return render(requst, template_name='list_documents.html', context={'pdfs': pdfs})


@login_required
def view_document(request):
    pdf_id = request.GET.get('pdf_id')
    pdf = PdfFile.objects.get(user=request.user, pdf_id=pdf_id)
    return render(request, template_name='view_document.html', context={'pdf': pdf})


@login_required
def delete_document(request):
    pdf_id = request.GET.get('pdf_id')
    pdf = PdfFile.objects.get(user=request.user, pdf_id=pdf_id)
    pdf.delete()
    return redirect('list_documents')


@login_required
def chat_view(request):
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

        llm_response = ""
        if form.is_valid():
            chat = build_chat(pdf_id)
            reply = chat.invoke({"input": form.cleaned_data['querry']})
            llm_response = reply["answer"]

        return render(request, 
                      template_name='chat_view.html', 
                      context={"pdf_path": pdf_path,
                               "llm_response": llm_response, 
                               "form": form})



