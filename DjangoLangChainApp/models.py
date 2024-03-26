from django.db import models
from django.contrib.auth.models import User
from .chat.pinecone.vector_store import pinecone_index
import os

class PdfFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pdf_id = models.UUIDField(primary_key=True, editable=False)
    pinecone_id_list = models.JSONField(default=list)   # List of vector ids associated with this pdf file
    
    
    def delete(self, *args, **kwargs):
        # Delete pinecone vectors
        pinecone_index.delete(ids=self.pinecone_id_list)
        # Delete from local storage
        os.remove(f"pdfs/{self.pdf_id}.pdf")
        super().delete(*args, **kwargs)
    
    def __str__(self) -> str:
        print("PdfFile: ", self.user, self.pdf_id)
        return super().__str__()
