from langchain_openai.chat_models import ChatOpenAI
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from ..pinecone.vector_store import get_retriever
from langchain import hub


def build_chat(pdf_id):
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    llm = ChatOpenAI(streaming=True)
    retriever = get_retriever(pdf_id)
    combine_docs_chain = create_stuff_documents_chain(
        llm, retrieval_qa_chat_prompt
    )
    return create_retrieval_chain(retriever, combine_docs_chain)

    
    
