from ..pinecone.vector_store import vector_store

def get_retriever(pdf_id):
    """
    Returns a Retriever instance that retrieves documents with the specified
    pdf_id. The Retriever can be used to retrieve documents from the
    vector_store.

    Parameters:
        pdf_id (UUID): The ID of the PDF document to retrieve.

    Returns:
        Retriever: A Retriever instance that retrieves documents with the
            specified pdf_id.
    """
    return vector_store.as_retriever(
        search_kwargs = {
            "filter": {"pdf_id": pdf_id.__str__()} # convert UUID to string
        }
    )
