from .views import *
from django.urls import path

urlpatterns = [
    path('', index, name='index'),
    path('accounts/register/', user_register, name='user_register'),
    path('accounts/login/', user_login, name='user_login'),
    path('accounts/logout/', user_logout, name='user_logout'),
    path('documents/upload/', upload_link, name='upload_link'),
    path('documents/list/', list_documents, name='list_documents'),
    path('documents/view/<uuid:pdf_id>/', view_document, name='view_document'),
    path('documents/delete/<uuid:pdf_id>/', delete_document, name='delete_document'),
    path('documents/chat/<uuid:pdf_id>/', chat_view, name='chat_view'),
]