from langchain.chat_models.openai import ChatOpenAI
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from .retriever import get_retriever
from langchain import hub


def build_chat(pdf_id):
    """
    Builds a chatbot using the specified PDF ID.

    Parameters:
        pdf_id (str): The ID of the PDF document to be used for chatbot training.

    Returns:
        RetrievalQAChatChain: The trained chatbot that can retrieve and answer questions based on the provided PDF document.
    """
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    llm = ChatOpenAI(streaming=True)
    retriever = get_retriever(pdf_id)
    combine_docs_chain = create_stuff_documents_chain(
        llm, retrieval_qa_chat_prompt
    )
    return create_retrieval_chain(retriever, combine_docs_chain)

    
    
