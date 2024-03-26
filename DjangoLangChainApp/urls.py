from django.urls import path
from .views import (index, 
                    user_register, 
                    user_login, 
                    user_logout, 
                    upload_link, 
                    list_documents, 
                    view_document, 
                    delete_document, 
                    chat_view)

urlpatterns = [
    path('', index, name='index'),
    path('user_register', user_register, name='user_register'),
    path('user_login', user_login, name='user_login'),
    path('user_logout', user_logout, name='user_logout'),
    path('upload_link', upload_link, name='upload_link'),
    path('list_documents', list_documents, name='list_documents'),
    path('view_document', view_document, name='view_document'),
    path('delete_document', delete_document, name='delete_document'),
    path('chat_view', chat_view, name='chat_view'),
]