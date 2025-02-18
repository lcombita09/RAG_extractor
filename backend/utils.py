import os
from dotenv import load_dotenv
from typing import List
import pathlib

from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document




## LOAD SECRETS

def load_secrets(secrets_files: List):
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    for secrets_file in secrets_files:
        secrets_file_path = os.path.join(parent_dir, '..', secrets_file)
        load_dotenv(secrets_file_path)

###############


## EMBEDDINGS MODEL

def get_embeddings_model():
    if "azure" in os.getenv("LLM_MODEL").lower():
        os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
        os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT")
        cloud_embeddings = AzureOpenAIEmbeddings(
            model=os.getenv("LLM_EMBEDDING_MODEL"),
        )
    elif "openai" in os.getenv("LLM_MODEL").lower():
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        cloud_embeddings = OpenAIEmbeddings()
    return cloud_embeddings
