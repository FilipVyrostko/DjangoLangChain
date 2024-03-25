from ..pinecone.vector_store import vector_store

def get_retriever(pdf_id):
    return vector_store.as_retriever(
        search_kwargs = {
            "filter": {"pdf_id": pdf_id.__str__()}
        }
    )
