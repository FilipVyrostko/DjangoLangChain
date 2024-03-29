import uuid
import os
from unittest.mock import patch
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import LinkUploadForm
from .views import upload_link
from .views import view_document
from .views import chat_view
from .models import PdfFile
from .forms import QueryForm
from langchain_core.runnables import Runnable


# Add mock.patches here to prevent creation of pdf files and writing to Pinecone
@patch('DjangoLangChainApp.views.add_documents_from_pdf', 
       return_value=["pinecone_id_1", "pinecone_id_2"])
@patch('DjangoLangChainApp.views.pdfkit.from_url', return_value=None)
class UploadLinkTestCase(TestCase):
    """Unit tests for the upload_link view."""

    def setUp(self):
        """Create a request factory for testing the view."""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        self.client.login(username='testuser', password='12345')

    def test_upload_link_get(self, *args):
        """Test GET request for upload_link view."""
        response = self.client.get('/documents/upload/')
        self.assertEqual(response.status_code, 200,
                         'Expected a 200 status code.')
        self.assertIsInstance(response.context['form'], LinkUploadForm,
                               'Expected a LinkUploadForm in the context.')

    def test_upload_link_post_valid_url(self, *args):
        """Test POST request for upload_link view with valid url."""
        response = self.client.post('/documents/upload/', {'url': 'https://example.com'})
        self.assertEqual(response.status_code, 302,
                         'Expected a 302 status code.')
        

    def test_upload_link_post_invalid_url(self, *args):
        """Test POST request for upload_link view with invalid url."""
        response = self.client.post('/documents/upload/', {'url': 'not a url'})
        self.assertEqual(response.status_code, 200,
                         'Expected a 200 status code.')
        self.assertIsNotNone(response.context['errors'])

    def test_upload_link_post_form_invalid(self, *args):
        """Test POST request for upload_link view with invalid form."""
        response = self.client.post('/documents/upload/', {})
        self.assertEqual(response.status_code, 200,
                         'Expected a 200 status code.')
        self.assertIsInstance(response.context['form'], LinkUploadForm,
                               'Expected a LinkUploadForm in the context.')
        self.assertTrue('errors' in response.context,
                        'Expected errors in the context.')


class ListDocumentsTestCase(TestCase):
    """
    Test suite for the list_documents view.
    """
    def setUp(self):
        """
        Set up the test environment by creating a user and initializing a client.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()

    def test_redirect_if_not_authenticated(self):
        """
        Test that the user is redirected to the login page if not authenticated.
        """
        response = self.client.get(reverse('list_documents'))
        self.assertRedirects(response, '/accounts/login/?next=%2Fdocuments%2Flist%2F')

    def test_return_correct_template_and_context(self):
        """
        Test that the view returns the correct template and empty context if the
        user is authenticated but no documents have been uploaded.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('list_documents'))
        self.assertTemplateUsed(response, 'list_documents.html')
        self.assertQuerySetEqual(response.context['pdfs'], [])

    def test_show_document_if_exists(self):
        """
        Test that the view shows the document if it exists.
        """
        pdf_id = uuid.uuid4()
        pdf = PdfFile.objects.create(user=self.user, 
                                     pdf_id=pdf_id, 
                                     pinecone_id_list=["pinecone_id1", "pinecone_id2"])
        pdf.save()
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('list_documents'))
        self.assertContains(response, pdf_id)


class ViewDocumentTestCase(TestCase):
    """
    Test suite for the view_document view.

    Tests that the view_document view requires login, retrieves the correct
    PDF document from the database, and renders the correct template with the
    PDF document in the context.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.pdf = PdfFile.objects.create(user=self.user, pdf_id=uuid.uuid4())
        self.client = Client()

    def test_login_required(self):
        """
        Test that the view_document view requires login.
        """
        response = self.client.get(reverse('view_document', args=[self.pdf.pdf_id]))
        self.assertRedirects(response, 
                             f'/accounts/login/?next=/documents/view/{self.pdf.pdf_id}/')
        
    def test_retrieves_correct_pdf_document(self):
        """
        Test that the view_document view retrieves the correct PDF document
        from the database.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('view_document', args=[self.pdf.pdf_id]))
        self.assertEqual(response.context['pdf'], self.pdf, 'Expected the PDF document in the context.')

    def test_renders_correct_template_with_pdf_document(self):
        """
        Test that the view_document view renders the correct template with the
        PDF document in the context.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('view_document', args=[self.pdf.pdf_id]))
        self.assertTemplateUsed(response, 'view_document.html', 'Expected view_document template.')


@patch("DjangoLangChainApp.models.pinecone_index.delete", return_value=True)
class DeleteDocumentTestCase(TestCase):
    """
    Tests that the delete_document view deletes the correct PDF document from
    the database, redirects the user to the list of documents view, and returns
    a 404 error for invalid pdf_id.
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.pdf = PdfFile.objects.create(user=self.user, pdf_id=uuid.uuid4())  # Create a test PDF file

    def test_delete_document_valid_pdf_id(self, *args):
        """
        Test that the delete_document view deletes the correct PDF document from
        the database and redirects the user to the list of documents view.
        """
        response = self.client.get(f"/documents/delete/{self.pdf.pdf_id}", follow=True)
        self.assertEqual(response.status_code, 200)  # Check if the document is deleted and user is redirected
        self.assertRedirects(response, reverse('list_documents'), status_code=301)
        self.assertFalse(PdfFile.objects.filter(pdf_id=self.pdf.pdf_id).exists())  # Check if document is deleted

    def test_delete_document_invalid_pdf_id(self, *args):
        """
        Test that a 404 error is returned for an invalid pdf_id.
        """
        response = self.client.get(f'/documents/delete/{uuid.uuid4()}', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Document not found", str(response.content))

    def test_delete_document_redirect(self, *args):
        """
        Test that the user is redirected to the list of documents view after
        deleting a document.
        """
        response = self.client.get(f'/documents/delete/{self.pdf.pdf_id}',
                                   follow=True)
        self.assertRedirects(response, reverse('list_documents'), status_code=301)  # Check if user is redirected to the list of documents view

# Add patch to prevent invokation of LLM
@patch.object(Runnable, "invoke", return_value={"answer": "answer"})
class ChatViewTestCase(TestCase):
    """
    Unit tests for the chat_view view.

    Tests that the view renders the correct template with the correct pdf path
    and form in the context when the GET request is valid.

    Tests that the view returns a 404 status code when the GET request has an
    invalid pdf_id.

    Tests that the view renders the correct template with the correct pdf path
    and form in the context when the POST request is valid.

    Tests that the view returns a 404 status code when the POST request has an
    invalid pdf_id.

    Tests that the view renders the correct template with the correct pdf path
    and form in the context when the POST request is invalid.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.pdf = PdfFile.objects.create(user=self.user, pdf_id=uuid.uuid4())
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')


    def test_chat_view_get_valid_pdf_id(self, *args):
        response = self.client.get(f'/documents/chat/{self.pdf.pdf_id}', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pdf_path'], f'pdfs/{self.pdf.pdf_id}.pdf')
        self.assertIsInstance(response.context['form'], QueryForm)
        self.assertTemplateUsed(response, 'chat_view.html')

    def test_chat_view_get_invalid_pdf_id(self, *args):
        response = self.client.get('/documents/chat/invalid_pdf_id')
        self.assertEqual(response.status_code, 404)

    def test_chat_view_post_valid_form_data(self, *args):
        response = self.client.post(f'/documents/chat/{self.pdf.pdf_id}/', 
                                    {'querry': 'test query'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pdf_path'], f'pdfs/{self.pdf.pdf_id}.pdf')
        self.assertIsInstance(response.context['form'], QueryForm)
        self.assertEqual(len(response.context['llm_response']), 2)
        self.assertEqual(response.context['llm_response'][0], 'test query')
        self.assertTemplateUsed(response, 'chat_view.html')

    def test_chat_view_post_invalid_form_data(self, *args):
        response = self.client.post(f'/documents/chat/{self.pdf.pdf_id}', 
                                    {'querry': ''},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pdf_path'], f'pdfs/{self.pdf.pdf_id}.pdf')
        self.assertIsInstance(response.context['form'], QueryForm)
        self.assertIn('errors', response.context)
        self.assertTemplateUsed(response, 'chat_view.html')

    def test_chat_view_post_invalid_pdf_id(self, *args):
        response = self.client.post('/documents/chat/invalid_pdf_id',
                                    {'querry': 'test query'},
                                    follow=True)
        self.assertEqual(response.status_code, 404)
