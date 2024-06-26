import os
from django.db import models
from django.contrib.auth.models import User
from .chat.pinecone.vector_store import pinecone_index

class PdfFile(models.Model):
    """
    Represents a PDF file uploaded by a user.

    Attributes:
        user (django.contrib.auth.models.User): The user who uploaded the PDF.
        pdf_id (uuid.UUID): The unique ID of the PDF file.
        pinecone_id_list (list[str]): List of vector IDs associated with this PDF.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pdf_id = models.UUIDField(primary_key=True, editable=False)
    # List of vector ids associated with this pdf file
    pinecone_id_list = models.JSONField(default=list)
    
    
    def delete(self, *args, **kwargs):
        """
        Delete this PDF file from the database and local storage.

        This method deletes this PDF file from the Pinecone vector store,
        deletes the PDF file from local storage, and then deletes this
        object from the Django database.

        Args:
            *args: Positional arguments to pass to the super method.
            **kwargs: Keyword arguments to pass to the super method.
        """

        pinecone_index.delete(ids=self.pinecone_id_list)
        
        pdf_path = f"pdfs/{self.pdf_id}.pdf"
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        # Delete this object from the Django db
        super().delete(*args, **kwargs)
    
    def __str__(self) -> str:
        """
        Return a string representation of this object.

        Returns:
            str: A human-readable string representation of this object.
        """
        print("PdfFile: ", self.user, self.pdf_id)
        return super().__str__()
