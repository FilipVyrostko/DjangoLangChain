from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.pdf import PyPDFLoader
from ..embeddings.embeddings import openai_embeddings
import os


pinecone = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
pinecone_index = pinecone.Index(os.environ["PINECONE_INDEX"])
vector_store = PineconeVectorStore(index=pinecone_index, embedding=openai_embeddings)

def add_documents_from_pdf(pdf_path, pdf_id):
    docs = PyPDFLoader(pdf_path).load_and_split(
        RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=1000,
            chunk_overlap=0,
        )
    )
    for doc in docs:
        doc.metadata = {
            "page": doc.metadata["page"],
            "text": doc.page_content,
            "pdf_id": pdf_id.__str__()  # need to convert UUID to string
        }
    return vector_store.add_documents(docs)

def get_retriever(pdf_id):
    return vector_store.as_retriever(
        search_kwargs = {
            "filter": {"pdf_id": pdf_id.__str__()}
        }
    )



