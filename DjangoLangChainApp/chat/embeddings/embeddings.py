from langchain_openai import OpenAIEmbeddings
import os

openai_embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])